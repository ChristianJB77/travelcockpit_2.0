# Travel Cockpit 2.0
#### Full Stack Web Developer CAPSTONE PROJECT
To finally be able to deploy my own web app, I took this Nanondegree. Based on my CS50 final project Flask app 'Travel Cockpit', I have rebuild the entire app to finally deploy it for desktop and mobile usage. As well added a travel suggestion blog functionality to share our personal 'travel secrets'.

## Purpose
As passionate travelers my wife and me were continuously looking for a central
Travel Cockpit to get all essential information necessary to plan a trip in one
tool or view. To avoid the tedious googling for each source and forgetting
always at least one important info.
Then especially in COVID-19 times it was waste of time to prepare long time
planned trips.
As nothing similar is existing, I have developed a Travel Cockpit, which makes
a spontaneous trip planning easy and efficient.

## Concept
User can search for his desired travel destination or get a suggestion of currently
warm places on the planet. The destination can be a country (German/English), city (English) or for a good
luck search any place/region.
To get inspired for new, but less mainstream targets, the user can browse the 'Travel Secrets'. The blog is managed by 2 roles: Manager (can create/edit/delete own secrets), Director (all rights).
Based on the user's search a desktop consisting of tailored widgets and direct link buttons appear. As the main target is to inform the user with all essential travel information in one view or one direct click away.

This Web (HTML) based dashboard, which works on a Smart TV, Desktop and mobile
device focuses the European and especially German traveler. Therefore the dashboard
search function works in German and English with language specific travel links.


Restore database for testing

 pg_restore -U postgres --dbname=travel_cockpit_test --verbose database/travel_cockpit_test.sql
