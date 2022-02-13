'''Code file for badminton elimination lab created for Advanced Algorithms
Spring 2021 at Olin College. The code for this lab has been adapted from:
https://github.com/ananya77041/baseball-elimination/blob/master/src/BaseballElimination.java'''

import sys
import math
import picos as pic
import networkx as nx
import itertools
import cvxopt


class Division:
    '''
    The Division class represents a badminton division. This includes all the
    teams that are a part of that division, their winning and losing history,
    and their remaining games for the season.

    filename: name of a file with an input matrix that has info on teams &
    their games
    '''

    def __init__(self, filename):
        self.teams = {}
        self.G = nx.DiGraph()
        self.readDivision(filename)

    def readDivision(self, filename):
        '''Reads the information from the given file and builds up a dictionary
        of the teams that are a part of this division.

        filename: name of text file representing tournament outcomes so far
        & remaining games for each team
        '''
        f = open(filename, "r")
        lines = [line.split() for line in f.readlines()]
        f.close()

        lines = lines[1:]
        for ID, teaminfo in enumerate(lines):
            # ID, teamname, wins, losses, remaining, against
            team = Team(int(ID), teaminfo[0], int(teaminfo[1]), int(teaminfo[2]), int(teaminfo[3]), list(map(int, teaminfo[4:])))
            self.teams[ID] = team

    def get_team_IDs(self):
        '''Gets the list of IDs that are associated with each of the teams
        in this division.

        return: list of IDs that are associated with each of the teams in the
        division
        '''
        return self.teams.keys()

    def is_eliminated(self, teamID, solver):
        '''Uses the given solver (either Linear Programming or Network Flows)
        to determine if the team with the given ID is mathematically
        eliminated from winning the division (aka winning more games than any
        other team) this season.

        teamID: ID of team that we want to check if it is eliminated
        solver: string representing whether to use the network flows or linear
        programming solver
        return: True if eliminated, False otherwise
        '''
        flag1 = False
        team = self.teams[teamID]

        temp = dict(self.teams)
        del temp[teamID]

        for _, other_team in temp.items():
            if team.wins + team.remaining < other_team.wins:
                flag1 = True

        self.create_network(teamID)
        if not flag1:
            if solver == "Network Flows":
                flag1 = self.network_flows()
            elif solver == "Linear Programming":
                flag1 = self.linear_programming()

        return flag1

    def create_network(self, teamID):
        '''Builds up the network needed for solving the badminton elimination
        problem as a network flows problem & stores it in self.G. Returns a
        dictionary of saturated edges that maps team pairs to the amount of
        additional games they have against each other.

        teamID: ID of team that we want to check if it is eliminated
        return: dictionary of saturated edges that maps team pairs to
        the amount of additional games they have against each other
        '''

        # make 1 network for the team with the given id
        # get team IDs for all teams
        all_teams = self.get_team_IDs
        # save team IDs for all but teamID
        other_team_IDs = []
        #other_teams_IDs = all_teams.remove(teamID)
        for team in all_teams != teamID:
            other_team_IDs.append(team)

        # add source node to G
        self.G.add_node("S")
        # add sink node to G
        self.G.add_node("T")
        # get combinations of teams
        other_team_combinations = itertools.combinations(other_team_IDs, 2)

        # create column of nodes before sink
        for team in other_team_IDs:
            self.G.add_node(team)

        # create column of nodes after source and generate edge values and shit
        for combo in other_team_combinations:
            # add node to G
            combo_name = combo[0]+"_"+combo[1]
            self.G.add_node(combo_name)
            # add edge between source and next node with value edge_value
            edge_value = combo[0].get_against(combo[1])
            # assuming order indicates direction
            self.G.add_edge("S", combo_name, edge_value)
            # add edges between middle columns
            self.G.add_edge(combo_name, combo[0], float('inf')) 
            self.G.add_edge(combo_name, combo[1], float('inf')) 

        # add edges from last column to sink
        for team in other_team_IDs:
            edge_value = teamID.wins + teamID.remaining - team.wins
            self.G.add_edge(team, "T", edge_value)

    def network_flows(self):
        '''Uses network flows to determine if the team with given team ID
        has been eliminated. You can feel free to use the built in networkx
        maximum flow function or the maximum flow function you implemented as
        part of the in class implementation activity.

        the amount of additional games they have against each other
        return: True if team is eliminated, False otherwise
        '''
        out_edges = G.out_edges('S') # 's' is source node
        source_out = 0 # sum of capacites of edges leaving the source
        for edge in out_edges:
            source_out += nx.maximum_flow_value(G, edge[0], edge[1])

        max_flow, flow_dict = nx.maximum_flow(G, 'S', 'T') # 's' is source, 't' is sink
        if source_out >= max_flow:
            return True # person has been eliminated
        else:
            return False # person has not been eliminated


    def linear_programming(self):
        '''Uses linear programming to determine if the team with given team ID
        has been eliminated. We recommend using a picos solver to solve the
        linear programming problem once you have it set up.
        Do not use the flow_constraint method that Picos provides (it does all of the work for you)
        We want you to set up the constraint equations using picos (hint: add_constraint is the method you want)

        the amount of additional games they have against each other
        returns True if team is eliminated, False otherwise
        '''

        maxflow=pic.Problem()

        #TODO: implement this
        # we recommend using the 'cvxopt' solver once you set up the problem

        return False


    def checkTeam(self, team):
        '''Checks that the team actually exists in this division.
        '''
        if team.ID not in self.get_team_IDs():
            raise ValueError("Team does not exist in given input.")

    def __str__(self):
        '''Returns pretty string representation of a division object.
        '''
        temp = ''
        for key in self.teams:
            temp = temp + f'{key}: {str(self.teams[key])} \n'
        return temp

class Team:
    '''
    The Team class represents one team within a badminton division for use in
    solving the badminton elimination problem. This class includes information
    on how many games the team has won and lost so far this season as well as
    information on what games they have left for the season.

    ID: ID to keep track of the given team
    teamname: human readable name associated with the team
    wins: number of games they have won so far
    losses: number of games they have lost so far
    remaining: number of games they have left this season
    against: dictionary that can tell us how many games they have left against
    each of the other teams
    '''

    def __init__(self, ID, teamname, wins, losses, remaining, against):
        self.ID = ID
        self.name = teamname
        self.wins = wins
        self.losses = losses
        self.remaining = remaining
        self.against = against

    def get_against(self, other_team=None):
        '''Returns number of games this team has against this other team.
        Raises an error if these teams don't play each other.
        '''
        try:
            num_games = self.against[other_team]
        except:
            raise ValueError("Team does not exist in given input.")

        return num_games

    def __str__(self):
        '''Returns pretty string representation of a team object.
        '''
        return f'{self.name} \t {self.wins} wins \t {self.losses} losses \t {self.remaining} remaining'

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        division = Division(filename)
        for (ID, team) in division.teams.items():
            print(f'{team.name}: Eliminated? {division.is_eliminated(team.ID, "Linear Programming")}')
    else:
        print("To run this code, please specify an input file name. Example: python badminton_elimination.py teams2.txt.")
