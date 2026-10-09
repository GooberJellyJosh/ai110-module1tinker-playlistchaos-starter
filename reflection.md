# Reflection

## 1. The issue I fixed

Search was broken. I typed "AC" in the Hype playlist and got no results, even though AC/DC was right there. The problem was in `search_songs` in `playlist_logic.py`. The check was backwards, so it looked for the artist name inside my search text when it should have looked for my search text inside the artist name. Swapping the two sides fixed it.

## 2. Using the AI assistant

- **What I asked:** I had it explain the project first, then gave it the intended behavior rules from the lab page so it knew what "correct" meant.
- **Context:** It read both files on its own. I had to tell it how I wanted the code to look, eg. real variable names and comments.
- **What I didn't just trust:** It added a duplicate song check based on how it read "unique count" in the rules, which is a guess about what the rule means. It also kept artists in lowercase because the rules say to, even though "ac/dc" looks off.

## 3. The refactor

It renamed short variables like `q` and `k`, moved the keyword lists into constants, and made one shared genre list where there used to be two copies. I kept what it suggested. The only part I looked at closely was removing two sidebar columns, but they were never actually used. I knew it was safe because the same tests passed before and after.

## 4. Testing

I checked search, adding songs, lucky pick in each mode, and the stats. 16 of 25 test cases passed before the fixes and all 25 passed after. No new bugs showed up. Two things are still a little weird: artists show in lowercase, and a low energy rock song still counts as Hype because Hype gets checked first.

## 5. One insight

Give the AI the rules for how the app should work before asking it to fix anything, and have it show the bug failing first. Then run the same test after the fix so you can see for yourself that it worked.
