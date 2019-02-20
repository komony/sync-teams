import sys, requests, json

# global vars
ROLE_MAINTAINER = "maintainer"
ROLE_MEMBER = "member"
GITHUB_API = "https://api.github.com"

def get_org(full_team):
    return (full_team.split("/")[0])

def get_team(full_team):
    return (full_team.split("/")[1])

def get_team_id(full_team, auth_token):
    r = requests.get(GITHUB_API + "/orgs/" + get_org(full_team) + "/teams", headers = {'Authorization': 'token ' + auth_token})
    if(r.ok):
        org_teams = json.loads(r.text or r.content)
        for team in org_teams:
            if team['name'] == get_team(full_team):
                return team["id"]
    return None

def get_team_users(team_id, auth_token, role):
    members = []
    r = requests.get(GITHUB_API + "/teams/" + str(team_id) + "/members?role=" + role, headers = {'Authorization': 'token ' + auth_token})
    if(r.ok):
        team_members = json.loads(r.text or r.content)
        for team_member in team_members:
            members.append(team_member["login"])     
    return members

def add_or_update_membership(team_id, username, auth_token, role):
    payload = {'role': role}
    r = requests.put(GITHUB_API + "/teams/" + str(team_id) + "/memberships/" + username, headers = {'Authorization': 'token ' + auth_token}, data = json.dumps(payload))
    if(not r.ok):
        raise Exception("Request failed with error: " + r.content)
    return True

def remove_membership(team_id, username, auth_token):
    r = requests.delete(GITHUB_API + "/teams/" + str(team_id) + "/memberships/" + username, headers = {'Authorization': 'token ' + auth_token})
    if(not r.ok):
        raise Exception("Request failed with error: " + r.content)
    return True

def format_and_print(user_list, role, action):
    if (len(user_list) > 0):
        string_joiner = ", "
        print("{0} {1}s {2}ed = {3}".format(len(user_list), role, action, string_joiner.join(user_list)))

def sync_teams(source_team, dest_team, auth_token):
    source_team_id = get_team_id(source_team, auth_token)
    dest_team_id = get_team_id(dest_team, auth_token)

    source_team_maintainers = get_team_users(source_team_id, auth_token, ROLE_MAINTAINER)
    source_team_members = get_team_users(source_team_id, auth_token, ROLE_MEMBER)
    dest_team_maintainers = get_team_users(dest_team_id, auth_token, ROLE_MAINTAINER)
    dest_team_members = get_team_users(dest_team_id, auth_token, ROLE_MEMBER)

    maintainers_added = []
    members_added = []
    maintainers_removed = []
    members_removed = []

    for source_team_maintainer in source_team_maintainers:
        if source_team_maintainer not in dest_team_maintainers:
            # add as maintainer to destination team
            add_or_update_membership(dest_team_id, source_team_maintainer, auth_token, ROLE_MAINTAINER)
            maintainers_added.append(source_team_maintainer)

    for source_team_member in source_team_members:
        if source_team_member not in dest_team_members:
            # add as member to destination team
            add_or_update_membership(dest_team_id, source_team_member, auth_token, ROLE_MEMBER)
            members_added.append(source_team_member)

    dest_team_maintainers = get_team_users(dest_team_id, auth_token, ROLE_MAINTAINER)
    dest_team_members = get_team_users(dest_team_id, auth_token, ROLE_MEMBER)

    for dest_team_maintainer in dest_team_maintainers:
        if dest_team_maintainer not in source_team_maintainers:
            # remove as maintainer from destination team
            remove_membership(dest_team_id, dest_team_maintainer, auth_token)
            maintainers_removed.append(dest_team_maintainer)

    for dest_team_member in dest_team_members:
        if dest_team_member not in dest_team_members:
            # remove as member from destination team
            remove_membership(dest_team_id, dest_team_member, auth_token)
            members_removed.append(dest_team_member)

    format_and_print(maintainers_added, ROLE_MAINTAINER, "add")
    format_and_print(members_added, ROLE_MEMBER, "add")
    format_and_print(maintainers_removed, ROLE_MAINTAINER, "remove")
    format_and_print(members_removed, ROLE_MEMBER, "remove")
    print("Teams have been synced")

source_team = sys.argv[1]   # org/teamname format
dest_team = sys.argv[2]     # org/teamname format
auth_token = sys.argv[3]    # auth token with admin:org scope (https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/)

if len(sys.argv) == 4:
    sync_teams(source_team, dest_team, auth_token)
else:
    print("Please use command in following format: python3 sync-teams.py '<SOURCE_TEAM>' '<DESTINATION_TEAM>' '<OAUTH_TOKEN>'")
