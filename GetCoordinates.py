import pyautogui
import time

print("Zet je muis op de plek waar het begin van het woord staat...")
time.sleep(5)
print("Coördinaten begin woord:", pyautogui.position())

print("Zet je muis op de plek waar het einde van het woord staat...")
time.sleep(5)
print("Coördinaten eind woord:", pyautogui.position())

print("Zet je muis op het invoerveld...")
time.sleep(5)
print("Coördinaten invoerveld:", pyautogui.position())
