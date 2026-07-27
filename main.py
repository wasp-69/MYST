import customtkinter as ctk
import threading
from google import genai
import os
from dotenv import load_dotenv
from random import randint
from datetime import datetime

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY") # get the API key from the .env file
client = genai.Client(api_key=API_KEY)
interactionID = None

primary_col = ("#C1BFBF", "#22242A")
secondary_col = ("#19017a", "#7383ff")
level_one_col = ("#D7D7D7","#2C2E35")
level_two_col = ("#e6e6e6","#373a42")
level_three_col = ("#ffffff","#44474f")

def get_reply(query):
    global interactionID

    current_persona = persona_box.get()
    reply_length = wordlimit_slider.get()

    prompt = f"You are MYST, a chatbot with {current_persona} persona, reply to this user's message in {reply_length} words: {query}"

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt,
        previous_interaction_id=interactionID)
    interactionID = interaction.id

    return interaction.output_text

def send_reply(query): # send the query to Gemini, get reply and make it appear on the window
    prog_bar = ctk.CTkProgressBar(messages_SF, 
                                  orientation="horizontal", 
                                  mode="indeterminate", 
                                  progress_color=secondary_col, 
                                  width=150 + randint(0,300))
    prog_bar.set(0)
    prog_bar.start()
    prog_bar.grid(column=0, padx=10, pady=10, sticky="w", ipady=10, ipadx=0) # show a progress bar while Gemini thinks

    bot_reply = get_reply(query)

    prog_bar.grid_forget() # remove the progress bar

    bot_message = ctk.CTkLabel(messages_SF,
                                text=bot_reply,
                                font=("Century Gothic",15),
                                anchor="w",
                                wraplength=260,
                                fg_color=secondary_col,
                                corner_radius=20,
                                justify="left",
                                text_color="#ffffff")
    bot_message.grid(column=0,padx=10,pady=(10,0), sticky="w", ipady=10, ipadx=0) # place the reply to the left

    now = datetime.now()
    timestamp = ctk.CTkLabel(messages_SF,
                                text=now.strftime("%H:%M:%S"),
                                font=("Century Gothic",10),
                                text_color="#868686",
                                fg_color="transparent",
                                justify="left")
    timestamp.grid(column=0, padx=10, pady=(0,10), sticky="w") # place the time

    send_button.configure(state="normal") 
    entry_box.configure(state="normal")
    entry_box.bind("<Return>", send_message) # unlock inputs

def send_message(event=None): # show the user message 
    query = entry_box.get()

    if query.strip():

        entry_box.delete(0, "end")

        send_button.configure(state="disabled")
        entry_box.configure(state="disabled")
        entry_box.unbind("<Return>") # lock inputs

        user_message = ctk.CTkLabel(messages_SF,
                                    text=query,
                                    font=("Century Gothic",15),
                                    anchor="e",
                                    wraplength=260,
                                    fg_color=secondary_col,
                                    corner_radius=20,
                                    justify="left",)
        user_message.grid(column=1, padx=10, pady=(10,0), sticky="e", ipady=10, ipadx=0) # place the user message

        now = datetime.now()
        timestamp = ctk.CTkLabel(messages_SF,
                                 text=now.strftime("%H:%M:%S"),
                                 font=("Century Gothic",10),
                                 text_color="#868686",
                                 fg_color="transparent",
                                 justify="right")
        timestamp.grid(column=1, padx=10, pady=(0,10), sticky="e") # place the time

        t = threading.Thread(target=send_reply, args=(query,)) 
        t.start() # create and start a threaded call of the bot's reply

def change_theme(value): # changes the theme
    ctk.set_appearance_mode(value)


# ----- root app -----

root = ctk.CTk()
root.title("MYST")
root.geometry("1200x600+0+0")
root.configure(fg_color=primary_col) 

root.grid_columnconfigure(1, weight=1) 
root.grid_rowconfigure(0, weight=1) 

# ----- sidebar (settings) -----

settings = ctk.CTkFrame(root, 
                        width=300, 
                        corner_radius=10, 
                        fg_color=level_one_col) 
settings.grid(row=0, column=0, padx=10, pady=10, sticky="news")

sidebar_label = ctk.CTkLabel(settings, 
                             width=300, 
                             height=20, 
                             text="S e t t i n g s", 
                             font=("Century Gothic", 20))
sidebar_label.grid(row=0, column=0, padx=10, pady=10)

# --- theme ---

theme_frame = ctk.CTkFrame(settings, 
                           width=300, 
                           corner_radius=10, 
                           fg_color=level_two_col)
theme_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

theme_label = ctk.CTkLabel(theme_frame, 
                           height=20, 
                           text="Theme", 
                           font=("Century Gothic", 20))
theme_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

theme_var = ctk.StringVar(value="System")
theme_SB = ctk.CTkSegmentedButton(theme_frame, 
                              values=["System","Light","Dark"], 
                              font=("Century Gothic", 15), 
                              variable=theme_var,
                              selected_color=secondary_col,
                              command=change_theme)
theme_SB.grid(row=1, column=0, padx=5, pady=10)

# --- persona ---

persona_frame = ctk.CTkFrame(settings, 
                             width=300, 
                             corner_radius=10, 
                             fg_color=level_two_col)
persona_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

persona_label = ctk.CTkLabel(persona_frame, 
                             height=20, 
                             text="Persona", 
                             font=("Century Gothic", 20))
persona_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

persona_var = ctk.StringVar(value="casual") # set the default to casual (internal)
persona_box = ctk.CTkComboBox(persona_frame, 
                              values=["casual","professional","funny","disrespectful","informative","creative"],
                              state="readonly",
                              font=("century gothic", 15),
                              dropdown_font=("century gothic", 15))
persona_box.set("casual") # set the default to casual (external)
persona_box.grid(row=1, column=0, padx=10, pady=10)

# --- word limit ---

wordlimit_frame = ctk.CTkFrame(settings, 
                               width=300, 
                               corner_radius=10, 
                               fg_color=level_two_col)
wordlimit_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

wordlimit_label = ctk.CTkLabel(wordlimit_frame, 
                               height=20, 
                               text="Reply Length", 
                               font=("Century Gothic", 20))
wordlimit_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

wordlimit_slider = ctk.CTkSlider(wordlimit_frame, 
                                 from_=10,
                                 to=100,
                                 number_of_steps=9,
                                 button_color=secondary_col)
wordlimit_slider.set(10)
wordlimit_slider.grid(row=1, column=0, padx=10, pady=10)

# ----- main (chat) -----

chat = ctk.CTkFrame(root, 
                    corner_radius=10, 
                    fg_color=level_one_col) 
chat.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="news")

chat.grid_columnconfigure(0, weight=1)

main_label = ctk.CTkLabel(chat, 
                          width=500, 
                          height=20, 
                          text="C h a t", 
                          font=("Century Gothic", 20),) 
main_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# --- messages ---

chat.rowconfigure(1, weight=1)

messages_SF = ctk.CTkScrollableFrame(chat, 
                                    corner_radius=10,
                                    fg_color=level_two_col, 
                                    scrollbar_button_color=secondary_col)
messages_SF.grid(row=1, column=0, padx=10, pady=(10,0), sticky="news")

messages_SF.columnconfigure(0, weight=1) # this contains the user messages
messages_SF.columnconfigure(1, weight=1) # this contains the bot replies

# --- entry (input) ---

entry_frame = ctk.CTkFrame(chat, corner_radius=10, fg_color="transparent") 
entry_frame.grid(row=2,column=0, padx=5, pady=0, sticky="sew")

entry_frame.grid_columnconfigure(0, weight=1)

entry_box = ctk.CTkEntry(entry_frame, 
                         width=700, 
                         placeholder_text="Type Your Thoughts", 
                         font=("Century Gothic", 15))
entry_box.grid(row=0, column=0,padx=5, pady=20, sticky="ew")
entry_box.bind("<Return>", send_message) # bind the enter key to send the message

send_button = ctk.CTkButton(entry_frame, width=100, text="SEND", font=("Century Gothic", 15), command=send_message, fg_color=secondary_col) # send button
send_button.grid(row=0, column=1, padx=5, pady=20, sticky="ew")

# ------- root main loop -------

root.mainloop() 

# added random progress bar width
# added time lables for messages
# added 3 more personas