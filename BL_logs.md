

# 01-25-23
* I should just use supabase. It's got graphql and a bunch of things setup.
* I can use django with supabase, but django is to do things locally. 
* or with an API/task, no need for graphql things since supabase takes care of that.
* What do I do about migration btw django + supabase?
    - local env -- local 
        - local should pull from remote
        - 
    - dev -- 


# BL Notes
* Youtube Chapters -- https://stackoverflow.com/questions/63821605/how-do-i-get-info-about-a-youtube-videos-chapters-from-the-api

* Youtube Transcript -- https://github.com/jdepoix/youtube-transcript-api


## YT transcription sumamrization packages needed
* google api -- https://github.com/googleapis/google-api-python-client
* getting transcriptions: https://github.com/jdepoix/youtube-transcript-api
* youtube py -- https://github.com/sns-sdks/python-youtube
* Chapters:
    - some YT have chapters in descript. Can scrape on "description"
    - [x] some are "auto-generated", need to use selenium

## speaker diarization with transcript
https://github.com/lablab-ai/Whisper-transcription_and_diarization-speaker-identification-/blob/main/transcribtion_diarization.ipynb



Playwright install deps
`sudo apt-get install libgtk-3-0 libgconf-2-4 libasound2 libxdamage1 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 libcairo-gobject2 libcairo2 libgdk-pixbuf-2.0-0 libdbus-glib-1-2 libxcursor1 `



## youtube api
https://www.googleapis.com/youtube/v3/channels?forUsername=thepassionatefew&part=snippet,id&key=AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY




# Strawberry graphql


## extensinos plus
https://github.com/blb-ventures/strawberry-django-plus

Query optimization
https://github.com/strawberry-graphql/strawberry-graphql-django/issues/75





## Supabase notes

 `supabase/seed.sql` gets seeded when supabase starts


Link to an active project
```
supabase login
supabase link --project-ref $PROJECT_ID
```

Pull from prod env to local
```
supabase db remote commit
```
* When there are local changes vs remote, you'd need to `supabase db push` of local to remote


Create a new local migration file:
`supabase migration new new_employee`


This command apply "migrations" in `supabase/migrations` folder to local database, but will RESET everything.
```
supabase db reset
```
* Django migration needs to be reapplied.
* How do you re-seed? 
* How can i dump and restore local db?


Auto diff creates migration file `supabase/migrations/<timestamp>_xxx.sql` by pulling in changes made from local GUI against already applied sql migrations to create a new sql file (so when you bring down and up db, you have the changes in sql)
```
supabase db diff -f xxx
```

### Workflow for supabase dev
#### Locally
* `supabase db remote commit` pulls down from prod to local dev into migrations/
* Changes made in GUI needs to apply auto diff and generate diffed .sql


* supabase storage/bucket is not part of the localmigration?
