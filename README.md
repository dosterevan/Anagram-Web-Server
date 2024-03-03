# UOCIS322 - Project 3 #
Evan Doster

edoster@uoregon.edu

Description; The program is a simple anagram game designed for English-learning students in elementary and middle school. It presents a list of words to students and an anagram. The anagram is a jumble of some of the words, which are randomly chosen. Students attempt to type words that can be created from the jumble. When a matching word is typed, it is added to a list of solved words.

The vocabulary word list is fixed for one invocation of the server, so multiple students connected to the same server will see the same vocabulary list but may have different anagrams.

## Getting started

`flask_vocab.py` runs the anagram game, with the template `vocab.html`. This example uses a conventional interaction through a form, interacting only when the user submits the form. The vocabulary and anagram are currently loaded using basic JINJA. What you're supposed to do is to change the form interaction into an AJAX interaction (using JQuery).

## FAQ
### What is `src`?
This is a sub-package which contains modules related to the game. You should not make any changes there, but feel free to review them to get a better understanding.

### What is `data`?
This directory contains a few word lists in the form of text files. You should not make any changes to the ones that already exist. However, you can add your own (but don't have to). You can change the word list file in your `credentials.ini`.
	 

## Authors

Michal Young, Ram Durairajan. Updated by Ali Hassani.
