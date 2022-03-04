# Imports
import base64
import random
import PySimpleGUI as sg
import PIL
from PIL import Image
import random
import csv
import os
import io

# GUI window parameters
window_theme = "DarkAmber"
window_title = "Guessing Game"

# Save path & player score
save_path = "save_data.csv"
score = 0

# The maximum number of guesses a user has per game
max_guesses = 3

# Images
input_image = os.path.join("tmp", "logos_original.jpg")
directory_path = os.path.join("tmp", "images")
extensions = ("png", "jpg", "gif")
height = 75
width = 100
transpose = False

index = 0
correct_guess = ""

logos = {
    "Pizza Hut" : [1, 2, 7, 8],
    "Dominos" : [3, 4, 9, 10],
    "Animal Planet" : [5, 6, 11, 12],
    "Spotify" : [13, 14, 19, 20],
    "Starbucks" : [15, 16, 21, 22],
    "Lufthansa" : [17, 18, 23, 24],
    "Apple" : [25, 26, 31, 32],
    "Wikipedia" : [27, 28, 33, 34],
    "WWF" : [29, 30, 35, 36]
}

def get_random_image():
    global correct_guess

    file = random.choice([os.path.join(directory_path, f) for f in os.listdir(directory_path) if True in [f.endswith(e) for e in extensions]])
    file_name = file.split(".")[0]
    index = int(file_name.split("-")[1])
    for k in logos:
        if index in logos[k]:
            correct_guess = k
            break
    return file

def convert_to_bytes(file_or_bytes, resize=None, fill=False):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height / cur_height, new_width / cur_width)
        img = img.resize((int(cur_width * scale), int(cur_height * scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

def crop(input_image, tile_width, tile_height, transpose: bool=False):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        if os.listdir(directory_path):
            return

    image = Image.open(input_image)
    image_width, image_height = image.size
    k = 0
    
    for x in range(image_width // tile_width):
        for y in range(image_height // tile_height):
            box = (y * tile_width, x * tile_height, (y+1) * tile_width, (x+1) * tile_height)
            tile = image.crop(box).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM) if transpose else image.crop(box)

            if not os.path.exists(directory_path):
                os.mkdir(directory_path)
            
            k += 1
            path = os.path.join(directory_path, f"Img-{k}.jpg")
            tile.save(path)

def save_data(path: str, *values: object):
    '''
Writes the data passed in the arg parameters to a csv file. 
Note: file mode "w+" opens a file for both writing and reading, and overwrites the existing file if it exists.
If the file does not exist, "w+" creates a new file.
    '''
    with open(path, "w+", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(values)

def load_data(path: str, default_value: object):
    '''
Checks if a path exists, and if it does, open the path and read the first value to return score. 
Otherwise, create a new csv file with the default score value
Note: file mode "r" opens a file for reading only.
    '''
    if not os.path.exists(path):
        save_data(path, default_value)
    
    with open(path, "r") as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def calculate_points(number_of_guesses: int):
    # Involves power for exponentially higher points for a first guess
    return int(36 / pow(number_of_guesses, 2))

def init_window():
    '''
Change window theme and define the window layout with game introduction, text, input field, output text, and buttons.
Then, create the window with the name and layout parameters.
    '''
    sg.theme(window_theme)
    
    file = get_random_image()
    # Note: do_not_clear set to false on the text input to automatically clear the input field when a button is pressed
    # Note: bind_return_key set to true on the "Ok" button to allow user to submit guess when hitting the return (enter) key
    layout = [  [sg.Text(f"Score: {score}", key="score")],
                [sg.Image(data=convert_to_bytes(file, (width*2,height*2)), pad=(width,20), key='image')],
                [sg.Text(f"What is the name of the entity with this logo? You have {max_guesses} tries!")],
                [sg.Text("Take a guess:", key="counter")],
                [sg.InputText(key="input", do_not_clear=False)],
                [sg.Text(size=(50,1), key="output")],
                [sg.Button("Ok", key="ok", bind_return_key=True), sg.Button("Restart")] ]

    # Note: Finalize the window in order to modify the window fields in reset_game() before reading the window
    return sg.Window(title=window_title, layout=layout, finalize=True), layout

def reset_game():
    # Define number and current_guess gloablly
    global number
    global current_guess

    # Reset current guess
    current_guess = 1
    #  Update guess counter
    window["counter"].update(f"Take a guess: ({current_guess} out of 3)")
    # Enable input field and ok button
    window["input"].update(disabled=False)
    window["ok"].update(disabled=False)

def main():
    '''
Set default number of points for a round to 0.
Get user input, then check whether the number is higher lower or the same.
If the number matches, congratulate the user, display the number of guesses, calculate points gained, 
and return out of the function with win condition as true and the number of points.
If the user can't guess the number within the max guesses, print out the chosen number, and return 0 points.
    '''
    global current_guess # Define that the variable current_guess being referenced is the global one
    points = 0

    user_guess = values["input"]
    
    if user_guess.lower() == correct_guess.lower():
        window["output"].update(f"Good job! You guessed the logo in {current_guess} guesses!")
        window["counter"].update("You won!") # Update the guess counter with the win condition

        # Calculate points depending on number of guesses
        points = calculate_points(current_guess)
        return True, points # Win condition (game ended)

    if current_guess >= max_guesses - 1:
        window["output"].update(f"Hint: The name begins with \"{correct_guess[0]}\"")
        return False, points # Game hasn't ended

    if current_guess >= max_guesses:
        window["output"].update(f"Unfortunately, you couldn't guess the logo! It was {correct_guess}")
        window["counter"].update("You lost!") # Update the guess counter with the win state
        return True, points # Win condition (game ended)

    # Increase current guess and update guess counter
    current_guess += 1
    window["counter"].update(f"Take a guess: ({current_guess} out of 3)")
    return False, points # Game hasn't ended


# Boilerplate that prevents users from accidentally invoking this script from another.
# Only runs when the current file is explicitly run.
if __name__ == "__main__":

    crop(input_image, width, height, transpose)

    # Load saved data. Default to 0 if file does not exist
    data = load_data(save_path, 0)
    
    # If list is not empty, assign saved score value
    if data:
        score = int(data[0][0])

    # Init window, then reset random number, current guess, guess counter, and enable input field and button
    window, layout = init_window()
    reset_game()

    # Infinite loop to keep the window open, unless the user closes the window
    while True:
        # Read events and values from the window object
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Cancel": # If user closes window or clicks cancel
            break
        elif event == 'Restart': # If user clicks restart
            # Clear output text field and reset game
            file = get_random_image()
            window["image"].update(data=convert_to_bytes(file, (width*2,height*2)))
            window["output"].update("")
            reset_game()
        else: # If user clicks ok
            # Check guess and store win condition
            win_condition, points = main()

            if win_condition: # If the game has ended
                # Disable input field and ok button
                window["input"].update(disabled=True)
                window["ok"].update(disabled=True)

                # Add game points to total score and save data in a csv
                score += points
                window["score"].update(f"Score: {score}")
                save_data(save_path, score)

    window.close() # Close the window once the loop is exited