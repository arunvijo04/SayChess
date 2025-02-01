import pygame
import chess
import chess.svg
import pyttsx3 
import speech_recognition as sr
import cairosvg
import io
from PIL import Image

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

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Valid chess squares for speech recognition filtering
valid_squares = [f"{file}{rank}" for file in "abcdefgh" for rank in "12345678"]

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)  # Noise reduction
        speak("Listening...")
        while True:
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

# Convert Chess Board to Pygame Image
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
    flagChance = 1
    print("Welcome to Speech Chess, let's begin!")
    speak("Welcome to Speech Chess, let's begin!")
    showBoard()

    while not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        print()
        if flagChance == 1:
            speak("White player's turn")
            flagChance = 0
        else:
            speak("Black player's turn")
            flagChance = 1
        
        def initial():
            speak("Enter the initial block")
            while True:
                initialBlock = takeCommand()
                try:
                    pieceFound = str(board.piece_at(chess.parse_square(initialBlock))).upper()
                    if pieceFound in ["P", "N", "R", "Q", "K", "B"]:
                        speak(f"Found {pieceFound} at {initialBlock}")
                        return initialBlock
                    else:
                        speak("No piece found, try again.")
                except Exception as e:
                    speak("Invalid square, please try again!")
                    print(e)
        
        def final():
            pieceFound1 = initial()
            speak("Enter the final block")
            while True:
                finalBlock = takeCommand()
                move = pieceFound1 + finalBlock
                try:
                    board.push_san(move)
                    showBoard()
                    break
                except Exception as e:
                    speak("Invalid move, please try again!")
                    print(e)

        final()

        if board.is_check():
            speak("Check")
        if board.is_checkmate():
            speak("Checkmate")
            break

    speak("Player 1, would you like to play again?")
    choice1 = takeCommand()
    speak("Player 2, would you like to play again?")
    choice2 = takeCommand()

    if choice1 == 'yes' and choice2 == 'yes':
        board.reset()
        game()

game()
pygame.quit()
