import pygame
import chess
import chess.svg
import pyttsx3
import speech_recognition as sr
import cairosvg
import io
import random
from PIL import Image
import time  
import sys


# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Speech Chess")

# Chess Board
board = chess.Board()

# Text-to-Speech Setup
engine = pyttsx3.init()
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

running = True  # Global flag for app status

def speak(text):
    if not running:
        return
    engine.say(text)
    engine.runAndWait()


# Valid squares for voice input
valid_squares = [f"{file}{rank}" for file in "abcdefgh" for rank in "12345678"]

def takeCommand():
    global running
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        speak("Listening...")
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

            try:
                audio = r.listen(source, timeout=None, phrase_time_limit=3)
                query = r.recognize_google(audio).lower().replace(" ", "")
                if query in valid_squares:
                    return query
                else:
                    speak("Invalid square, please try again.")
            except sr.UnknownValueError:
                speak("Could not understand, please repeat.")
            except sr.RequestError:
                speak("Speech service is unavailable, try again later.")
                return ""


# Render board using cairo and PIL
def render_board():
    svg = chess.svg.board(board)
    png = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
    image = Image.open(io.BytesIO(png))
    image = image.resize((WIDTH, HEIGHT))
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

def showBoard():
    screen.blit(render_board(), (0, 0))
    pygame.display.flip()

def game():
    print("Welcome to Speech Chess! You are playing as White.")
    speak("Welcome to Speech Chess! You are playing as White.")
    showBoard()

    running = True
    while running and not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if not running:
            break

        # Player (White) Turn
        if board.turn == chess.WHITE:
            speak("Your turn. Please say the initial square.")
            while True:
                initial = takeCommand()
                if not initial:  # if speech failed or was cancelled
                    running = False
                    break
                try:
                    piece = board.piece_at(chess.parse_square(initial))
                    if piece and piece.color == chess.WHITE:
                        speak(f"{piece.symbol().upper()} at {initial}. Now say the final square.")
                        break
                    else:
                        speak("No valid piece found. Try again.")
                except:
                    speak("Invalid square. Try again.")
            if not running:
                break

            while True:
                final = takeCommand()
                if not final:
                    running = False
                    break
                move_str = initial + final
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in board.legal_moves:
                        board.push(move)
                        showBoard()
                        break
                    else:
                        speak("Illegal move. Try again.")
                except:
                    speak("Invalid input. Try again.")
            if not running:
                break

        # AI (Black) Turn
        else:
            speak("AI is thinking...")
            time.sleep(1.5)

            ai_move = random.choice(list(board.legal_moves))
            move_san = board.san(ai_move)
            board.push(ai_move)
            showBoard()
            time.sleep(0.8)
            speak(f"AI moved {move_san}")

        # Check/checkmate notification
        if board.is_checkmate():
            speak("Checkmate!")
            break
        elif board.is_check():
            speak("Check!")

        if running:
            speak("Game over.")

            engine.stop()        # Stop any queued speech
            pygame.quit()
            sys.exit()


game()
pygame.quit()
