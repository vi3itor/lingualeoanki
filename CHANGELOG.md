# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
Section to track upcoming changes 

## [2.0.0] - 2019-04-07
### Added
- Full support of Anki 2.1.x and (at least) Anki 2.0.52.
- Ability to import not only all words, but words from one or several user dictionaries.
- Log in and log out buttons and ability to stay logged in (by storing cookies in the user_files folder).
- Import 'Studied', 'Unstudied' or 'Any' words.
- Option to update existing notes (otherwise check for duplicates first).
- Configuration file to store user's login and (optionally) password as well as other settings (stay logged in, protocol, remember the password)
- Six.py module for write Python 2 and 3 compatible code easier.
- Changelog to keep updates and changes in one place.

### Changed
- Check for duplicates before starting to download media (don't check for duplicates only if "Update existing notes" option is selected).
- Prevent multiple runs of the plugin at the same time.
- When exiting allow Anki's main window to close add-on window if no words are downloading.

### Removed
- Option "missed words": by default the add-on only downloads media for the words that are not in the deck.

## [1.3.1] - 2019-01-04
### Changed
- Fixed crash on first run caused by "missed" words option.

## [1.3.0] - 2018-11-11
### Added
- Option to download "missed" words: continue downloading from last downloaded word.

## [1.2.0] - 2018-01-25
### Added
- Support for words with apostrophes.

### Changed
- Update pictures and sound for duplicate words only if they are different.

## [1.1.0] - 2018-01-06
### Added
- Check for duplicates while adding new words.
- Retry downloading pictures and sound for notes if initially failed. 

## [1.0.0] - 2017-12-28
### Added
- Download words from user's dictionary in LinguaLeo.
- Option to download unstudied words only.
