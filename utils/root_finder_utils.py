


# the idea is  the following:
# user wants to redir or provide smth like this: localhost  /select/Sys_Services, where in Harvested_Routes
# you will find only /select/<*>. Having in mind we could potentially have /selec or whatever, we need to find as close
# match to what user wants as possible
# for now I suggest a very unneficient loop through routes from db character by character with a final result a table with matches.
# Then, the best match is returned

def find_valid_route():
    pass