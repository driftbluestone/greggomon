import discord, random
from modules import autocorrect, hints, stats, image_logic
from modules.updater import *
from modules.data import *

async def answer_logic(interaction: discord.Interaction, guess: str, bot):
    server_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    server: Server
    server = await get_server_object(server_id)
    user = await get_user_object(str(interaction.user.id), interaction.user.name)

    # stat tracking variables
    increment_server = []
    increment_user = []

    guess_list = autocorrect.correct_input(guess).split()
    words_found = []
    answer_wrong = False
    for item in guess_list:
        if item in server.answer_list:
            words_found.append(item)
        else:
            answer_wrong = True
    words_found.sort()
    server.answer_list.sort()

    server.guesses[user_id] = server.guesses.get(user_id, 0)
    if server.guesses[user_id] == server.config["user_guess_limit"]:
        return await interaction.response.send_message("You're out of guesses!")
    # hint logic. Eventually move to seperate python file!
    server.guess_counter+=1
    server.words_found.extend(words_found)

    hint = hints.get_hint(server)
    if server.guess_counter == server.config["guesses_to_hint"]:
        increment_server.append("hint_sent")
        possible_hints = [x for x in server.answer_list if x not in server.words_found]
        if not possible_hints:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nAll of the words in the item name have been found already.\n"
        else:
            hint = f"{server.config["guesses_to_hint"]} incorrect Guesses, huh? Heres a hint.\nOne of the words in the item name is: '{random.choice(possible_hints)}'\n"
    user_guess = ""
    if (words_found == server.answer_list) and (answer_wrong == False):
        increment_server.append("correct_guess")
        increment_user.append("correct_guess")
        server.guess_counter = 0
        server.words_found = []
        server.guesses = {}
        stats.increment_server_stats(server, user, increment_server, global_stats)
        stats.increment_user_stats(server, user, increment_user, global_leaderboard)
        await image_logic.send_image(interaction, f"'{autocorrect.uppercase(server.answer)}' is correct!\nMoving on the the next image...", True, bot)
        return
    elif len(words_found) != 0 and server.config["show_correct_words_on_partial_correct"]:
        increment_server.append("incorrect_guess")
        increment_user.append("incorrect_guess")
        if not server.config["hide_user_guesses"]:
            user_guess = f"Your guess was: '{guess}'"
        await interaction.response.send_message(f"Not quite! Correct words: {words_found}\n{hint}{user_guess}", ephemeral=server.config["hide_user_guesses"])
    else:
        increment_server.append("incorrect_guess")
        increment_user.append("incorrect_guess")
        if not server.config["hide_user_guesses"]:
            user_guess = f"Your guess was: '{guess}'"
        await interaction.response.send_message(f"Nope!\n{hint}{user_guess}", ephemeral=server.config["hide_user_guesses"])
    server.guesses[user_id] += 1
    stats.increment_server_stats(server, user, increment_server, global_stats)
    stats.increment_user_stats(server, user, increment_user, global_leaderboard)
    await save_server_state(server_id, server.config["global_scoreboard"])
    await save_user_state(user_id)