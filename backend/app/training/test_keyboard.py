# # test_keyboard.py
# import keyboard

# print("Press ESC to stop.")

# # This will run until you press ESC
# keyboard.wait('esc')


from pynput import keyboard

def on_press(key):
    print(f"Key {key} pressed")

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
