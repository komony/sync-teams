# sync-teams
Sync GitHub Teams Across Orgs (or same org)

Simple GitHub Utility script that utilizes the Org, Team and Memberships API of GitHub to sync two teams within the same or different org as long as the person running it has the token of an admin of both teams. The script maintains the role of the members while copying them to the new team - so both teams will have the same set of maintainers and members. 

To run the script, use the following command format:
`python 3 sync-teams.py "<SOURCE_TEAM>" "<DESTINATION_TEAM>" <OAUTH_TOKEN>`

### NOTES:
Please provide `<SOURCE_TEAM>` & `<DESTINATION_TEAM> in format `<org-name>/<team-name>`
Use an Oauth token for an owner (of both teams) with `admin:org` scope so that the script can add and remove team members. Instructions for creating a personal token is available here: https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/

For eg: `python 3 sync-teams.py "some-org/team name" "some-org/team name 2" somerandomtoken`
