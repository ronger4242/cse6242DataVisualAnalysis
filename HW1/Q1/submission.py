import http.client
import json
import csv


#############################################################################################################################
# cse6242 
# All instructions, code comments, etc. contained within this notebook are part of the assignment instructions.
# Portions of this file will auto-graded in Gradescope using different sets of parameters / data to ensure that values are not
# hard-coded.
#
# Instructions:  Implement all methods in this file that have a return
# value of 'NotImplemented'. See the documentation within each method for specific details, including
# the expected return value
#
# Helper Functions:
# You are permitted to write additional helper functions/methods or use additional instance variables within
# the `Graph` class or `TMDbAPIUtils` class so long as the originally included methods work as required.
#
# Use:
# The `Graph` class  is used to represent and store the data for the TMDb co-actor network graph.  This class must
# also provide some basic analytics, i.e., number of nodes, edges, and nodes with the highest degree.
#
# The `TMDbAPIUtils` class is used to retrieve Actor/Movie data using themoviedb.org API.  We have provided a few necessary methods
# to test your code w/ the API, e.g.: get_movie_cast(), get_movie_credits_for_person().  You may add additional
# methods and instance variables as desired (see Helper Functions).
#
# The data that you retrieve from the TMDb API is used to build your graph using the Graph class.  After you build your graph using the
# TMDb API data, use the Graph class write_edges_file & write_nodes_file methods to produce the separate nodes and edges
# .csv files for use with the Argo-Lite graph visualization tool.
#
# While building the co-actor graph, you will be required to write code to expand the graph by iterating
# through a portion of the graph nodes and finding similar artists using the TMDb API. We will not grade this code directly
# but will grade the resulting graph data in your Argo-Lite graph snapshot.
#
#############################################################################################################################


class Graph:

    # Do not modify
    def __init__(self, with_nodes_file=None, with_edges_file=None):
        """
        option 1:  init as an empty graph and add nodes
        option 2: init by specifying a path to nodes & edges files
        """
        self.nodes = []
        self.edges = []
        if with_nodes_file and with_edges_file:
            nodes_CSV = csv.reader(open(with_nodes_file))
            nodes_CSV = list(nodes_CSV)[1:]
            self.nodes = [(n[0], n[1]) for n in nodes_CSV]

            edges_CSV = csv.reader(open(with_edges_file))
            edges_CSV = list(edges_CSV)[1:]
            self.edges = [(e[0], e[1]) for e in edges_CSV]


    def add_node(self, id: str, name: str) -> None:
        """
        add a tuple (id, name) representing a node to self.nodes if it does not already exist
        The graph should not contain any duplicate nodes
        """
        newNode = (id, name)
        found = False
        
        for node in self.nodes:
            if node == newNode:
                found = True
                break

        if not found:    
            self.nodes.append(newNode)


    def add_edge(self, source: str, target: str) -> None:
        """
        Add an edge between two nodes if it does not already exist.
        An edge is represented by a tuple containing two strings: e.g.: ('source', 'target').
        Where 'source' is the id of the source node and 'target' is the id of the target node
        e.g., for two nodes with ids 'a' and 'b' respectively, add the tuple ('a', 'b') to self.edges
        """
        if source != target:
            newEdge = (source, target)
            newEdge2 = (target, source)
            found = False
            for edge in self.edges:
                if edge == newEdge or edge == newEdge2:
                    found = True
                    break
            if not found:
                self.edges.append(newEdge)
        


    def total_nodes(self) -> int:
        """
        Returns an integer value for the total number of nodes in the graph
        """
        return len(self.nodes)


    def total_edges(self) -> int:
        """
        Returns an integer value for the total number of edges in the graph
        """
        return len(self.edges)


    def max_degree_nodes(self) -> dict:
        """
        Return the node(s) with the highest degree
        Return multiple nodes in the event of a tie
        Format is a dict where the key is the node_id and the value is an integer for the node degree
        e.g. {'a': 8}
        or {'a': 22, 'b': 22}
        """
        d = {}
        for e in self.edges:
            if not e[0] in d:
                d[e[0]]= 0
            if not e[1] in d:
                d[e[1]] = 0
            d[e[0]] += 1
            d[e[1]] += 1
            
        max_degree = 0
        for key in d.keys():
            if d[key] > max_degree:
                max_degree = d[key]

        output = {}
        for key in d.keys():
            if d[key] == max_degree:
                output[key] = max_degree
        
        return output


    def print_nodes(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.nodes)


    def print_edges(self):
        """
        No further implementation required
        May be used for de-bugging if necessary
        """
        print(self.edges)


    # Do not modify
    def write_edges_file(self, path="edges.csv")->None:
        """
        write all edges out as .csv
        :param path: string
        :return: None
        """
        edges_path = path
        edges_file = open(edges_path, 'w', encoding='utf-8')

        edges_file.write("source" + "," + "target" + "\n")

        for e in self.edges:
            edges_file.write(e[0] + "," + e[1] + "\n")

        edges_file.close()
        print("finished writing edges to csv")


    # Do not modify
    def write_nodes_file(self, path="nodes.csv")->None:
        """
        write all nodes out as .csv
        :param path: string
        :return: None
        """
        nodes_path = path
        nodes_file = open(nodes_path, 'w', encoding='utf-8')

        nodes_file.write("id,name" + "\n")
        for n in self.nodes:
            nodes_file.write(str(n[0]) + "," + str(n[1]) + "\n")
        nodes_file.close()
        print("finished writing nodes to csv")


import http.client
import json
import csv

apiKey = '8788b2d55737d1f9acdb018ee1cfd192'

class  TMDBAPIUtils:

    # Do not modify
    def __init__(self, api_key:str):
        self.api_key=api_key


    def get_movie_cast(self, movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
        """
        Get the movie cast for a given movie id, with optional parameters to exclude an cast member
        from being returned and/or to limit the number of returned cast members
        documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

        :param integer movie_id: a movie_id
        :param integer limit: maximum number of returned cast members by their 'order' attribute
            e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
            If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range). 
            If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
            If after excluding, the limit is not specified, then return all remaining cast members."
            e.g., if limit=5 and the actor whose id corresponds to cast member with order=5 is to be excluded,
            return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
        :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
            e.g., if exclude_ids are [353, 455] then exclude these from any result.
        :rtype: list
            return a list of dicts, one dict per cast member with the following structure:
                [{'id': '97909' # the id of the cast member
                'character': 'John Doe' # the name of the character played
                'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
                Note that this is an example of the structure of the list and some of the fields returned by the API.
                The result of the API call will include many more fields for each cast member.

        Important: the exclude_ids processing should occur prior to limiting output.
        """
        
       
        conn = http.client.HTTPConnection("api.themoviedb.org")
        conn.request("GET", "/3/movie/{0}/credits?api_key = {1}".format(movie_id, self.api_key))
        response = conn.getresponse()

        movie_cast = []
        if response.status == 200:
            movie_data = response.read()
            movie_data_list = json.loads(movie_data.decode('utf-8'))
            movie_cast = movie_data_list['cast']
        
        if limit:
            mc_order_filter = [d for d in movie_cast if d['order'] < limit]
            movie_cast = mc_order_filter
        
        if exclude_ids:
            mc_ID_filter = [d for d in movie_cast if d['id'] not in exclude_ids] #filter the excluded ids
            movie_cast = mc_ID_filter
            
        movie_cast_list = []
        for movie in movie_cast: #retrieve only three pieces of info from the dictionary
            movie_cast_short = {
              "id": movie['id'],
              "name":movie['name'],
              "character": movie['character'],
              "credit_id": movie['credit_id'],
              "order": movie['order']
            }
            
            movie_cast_list.append(movie_cast_short)
        
        return movie_cast_list
        



    def get_movie_credits_for_person(self, person_id:str, vote_avg_threshold:float=None)->list:
            """
            Using the TMDb API, get the movie credits for a person serving in a cast role
            documentation url: https://developers.themoviedb.org/3/people/get-person-movie-credits
    
            :param string person_id: the id of a person
            :param vote_avg_threshold: optional parameter to return the movie credit if it is >=
                the specified threshold.
                e.g., if the vote_avg_threshold is 5.0, then only return credits with a vote_avg >= 5.0
            :rtype: list
                return a list of dicts, one dict per movie credit with the following structure:
                    [{'id': '97909' # the id of the movie credit
                    'title': 'Long, Stock and Two Smoking Barrels' # the title (not original title) of the credit
                    'vote_avg': 5.0 # the float value of the vote average value for the credit}, ... ]
            """
            conn = http.client.HTTPConnection("api.themoviedb.org")
            conn.request("GET", "/3/person/{0}/movie_credits?api_key = {1}".format(person_id, self.api_key))
            response = conn.getresponse()
    
            #person_movie = []
            if response.status == 200:
                person_movie_data = response.read()
                person_movie_data_list = json.loads(person_movie_data.decode('utf-8'))
                person_movie = person_movie_data_list['cast']
                #keys = person_movie_data_list.keys() #['cast', 'crew', 'id']
            person_movie_list = []
            for person in person_movie:
                person_movie_list_dict = {"id": person["id"], 
                                     "title": person["title"],
                                     "vote_avg": person["vote_average"]}
                person_movie_list.append(person_movie_list_dict)
            
            person_movie_threshold = []
            if vote_avg_threshold:
                for person_movie in person_movie_list:
                    if person_movie['vote_avg'] >= vote_avg_threshold:
                        person_movie_threshold.append(person_movie)
                return person_movie_threshold
            return person_movie_list          

#tmdb_api_utils = TMDBAPIUtils(apiKey)
#test_m1 = tmdb_api_utils.get_movie_cast(movie_id = '4785', limit=5)
#test_m1 
api_key = '545d1a716749141e976a42299993dbc8'
def get_movie_credits_for_person(person_id:str, vote_avg_threshold:float=None)->list:
    conn = http.client.HTTPConnection("api.themoviedb.org")
    conn.request("GET", "/3/person/{0}/movie_credits?api_key = {1}".format(person_id, api_key))
    response = conn.getresponse()
    
            #person_movie = []
    if response.status == 200:
        person_movie_data = response.read()
        person_movie_data_list = json.loads(person_movie_data.decode('utf-8'))
        person_movie = person_movie_data_list['cast']
        #keys = person_movie_data_list.keys() #['cast', 'crew', 'id']
    person_movie_list = []
    for person in person_movie:
        person_movie_list_dict = {"id": person["id"], 
                             "title": person["title"],
                             "vote_avg": person["vote_average"]}
        person_movie_list.append(person_movie_list_dict)
    
    person_movie_threshold = []
    if vote_avg_threshold:
        for person_movie in person_movie_list:
            if person_movie['vote_avg'] >= vote_avg_threshold:
                person_movie_threshold.append(person_movie)
        return person_movie_threshold
    return person_movie_list          
laurence_movie_Nancy = get_movie_credits_for_person(person_id="2975", vote_avg_threshold=8)
len(laurence_movie_Nancy)
#apiKey = '8788b2d55737d1f9acdb018ee1cfd192'
#tmdb_api_utils = TMDBAPIUtils(apiKey)
#test_m2 = tmdb_api_utils.get_movie_credits_for_person(person_id = '2', vote_avg_threshold = 8)
#test_m2

def get_movie_cast(movie_id:str, limit:int=None, exclude_ids:list=None) -> list:
    """
    Get the movie cast for a given movie id, with optional parameters to exclude an cast member
    from being returned and/or to limit the number of returned cast members
    documentation url: https://developers.themoviedb.org/3/movies/get-movie-credits

    :param integer movie_id: a movie_id
    :param integer limit: maximum number of returned cast members by their 'order' attribute
        e.g., limit=5 will attempt to return the 5 cast members having 'order' attribute values between 0-4
        If after excluding, there are fewer cast members than the specified limit, then return the remaining members (excluding the ones whose order values are outside the limit range). 
        If cast members with 'order' attribute in the specified limit range have been excluded, do not include more cast members to reach the limit.
        If after excluding, the limit is not specified, then return all remaining cast members."
        e.g., if limit=5 and the actor whose id corresponds to cast member with order=5 is to be excluded,
        return cast members with order values [0, 2, 3, 4], not [0, 2, 3, 4, 5]
    :param list exclude_ids: a list of ints containing ids (not cast_ids) of cast members  that should be excluded from the returned result
        e.g., if exclude_ids are [353, 455] then exclude these from any result.
    :rtype: list
        return a list of dicts, one dict per cast member with the following structure:
            [{'id': '97909' # the id of the cast member
            'character': 'John Doe' # the name of the character played
            'credit_id': '52fe4249c3a36847f8012927' # id of the credit, ...}, ... ]
            Note that this is an example of the structure of the list and some of the fields returned by the API.
            The result of the API call will include many more fields for each cast member.

    Important: the exclude_ids processing should occur prior to limiting output.
    """
    
   
    conn = http.client.HTTPConnection("api.themoviedb.org")
    conn.request("GET", "/3/movie/{0}/credits?api_key = {1}".format(movie_id, api_key))
    response = conn.getresponse()

    movie_cast = []
    if response.status == 200:
        movie_data = response.read()
        movie_data_list = json.loads(movie_data.decode('utf-8'))
        movie_cast = movie_data_list['cast']
    
    if limit:
        mc_order_filter = [d for d in movie_cast if d['order'] < limit]
        movie_cast = mc_order_filter
    
    if exclude_ids:
        mc_ID_filter = [d for d in movie_cast if d['id'] not in exclude_ids] #filter the excluded ids
        movie_cast = mc_ID_filter
        
    movie_cast_list = []
    for movie in movie_cast: #retrieve only three pieces of info from the dictionary
        movie_cast_short = {
          "id": movie['id'],
          "name":movie['name'],
          "character": movie['character'],
          "credit_id": movie['credit_id'],
          "order": movie['order']
        }
        
        movie_cast_list.append(movie_cast_short)
    
    return movie_cast_list
    
get_movie_cast(movie_id = 603, limit = 3)
# =============================================================================


#############################################################################################################################
#
# BUILDING YOUR GRAPH
#
# Working with the API:  See use of http.request: https://docs.python.org/3/library/http.client.html#examples
#
# Using TMDb's API, build a co-actor network for the actor's/actress' highest rated movies
# In this graph, each node represents an actor
# An edge between any two nodes indicates that the two actors/actresses acted in a movie together
# i.e., they share a movie credit.
# e.g., An edge between Samuel L. Jackson and Robert Downey Jr. indicates that they have acted in one
# or more movies together.
#
# For this assignment, we are interested in a co-actor network of highly rated movies; specifically,
# we only want the top 3 co-actors in each movie credit of an actor having a vote average >= 8.0.
# Build your co-actor graph on the actor 'Laurence Fishburne' w/ person_id 2975.
#
# You will need to add extra functions or code to accomplish this.  We will not directly call or explicitly grade your
# algorithm. We will instead measure the correctness of your output by evaluating the data in your argo-lite graph
# snapshot.
#
# GRAPH SIZE
# With each iteration of your graph build, the number of nodes and edges grows approximately at an exponential rate.
# Our testing indicates growth approximately equal to e^2x.
# Since the TMDB API is a live database, the number of nodes / edges in the final graph will vary slightly depending on when
# you execute your graph building code. We take this into account by rebuilding the solution graph every few days and
# updating the auto-grader.  We establish a bound for lowest & highest encountered numbers of nodes and edges with a
# margin of +/- 100 for nodes and +/- 150 for edges.  e.g., The allowable range of nodes is set to:
#
# Min allowable nodes = min encountered nodes - 100
# Max allowable nodes = max allowable nodes + 100
#
# e.g., if the minimum encountered nodes = 507 and the max encountered nodes = 526, then the min/max range is 407-626
# The same method is used to calculate the edges with the exception of using the aforementioned edge margin.
# ----------------------------------------------------------------------------------------------------------------------
# BEGIN BUILD CO-ACTOR NETWORK
#
# INITIALIZE GRAPH
#   Initialize a Graph object with a single node representing Laurence Fishburne
#
# BEGIN BUILD BASE GRAPH:
#   Find all of Laurence Fishburne's movie credits that have a vote average >= 8.0
#tmdb_api_utils = TMDBAPIUtils(apiKey)
#Laurence_movies = tmdb_api_utils.get_movie_credits_for_person(person_id = '2975', vote_avg_threshold = 8)
#Laurence_movies #

#get Laurence's movie ids
# =============================================================================
# LF_movie_ids = []
# for person_movie in Laurence_movies:
#     LF_movie_ids.append(person_movie['id'])
# LF_movie_ids #Laurence's movie_ids: [603, 813858, 503880, 684426, 201335, 28, 4539, 37757]
# 
# #   FOR each movie credit:
# #   |   get the movie cast members having an 'order' value between 0-2 (these are the co-actors)
# LF_movie_cast_members = [] #top 3 co-actors for each movie that Laurence has participated.
# for LF_movie_id in LF_movie_ids:
#     LF_movie_cast_ele= tmdb_api_utils.get_movie_cast(movie_id = LF_movie_id, limit=3)
#     for ele in LF_movie_cast_ele:
#         LF_movie_cast_members.append((ele['id'], ele['name']))
# LF_movie_cast_members #top 3 co-actors for each movie that Laurence has participated.
# len(LF_movie_cast_members) #22 actors in total, among which 4 are laurence, thus 18 co-actors in total
# 
# graph = Graph()
# for id_name in LF_movie_cast_members:
#     cast_id = id_name[0]
#     cast_name = id_name[1]
#     graph.add_node(cast_id, cast_name)
#     graph.add_edge(source="2975", target=cast_id)
# 
# graph.nodes
# graph.edges
# 
# =============================================================================

def get_actor_movie_ids(person_id):
    tmdb_api_utils = TMDBAPIUtils(apiKey)
    actor_movies= tmdb_api_utils.get_movie_credits_for_person(person_id = str(person_id), vote_avg_threshold = 8)
    actor_movie_ids = []
    for person_movie in actor_movies:
        actor_movie_ids.append(person_movie['id'])
    return actor_movie_ids

#get_actor_movie_ids(2975)#get node's movie ids
#get_actor_movie_ids(6384)

def get_top3_coactors(person_id):
    actor_movie_cast_members = [] #top 3 co-actors for each movie that an actor has participated.
    actor_movie_ids = get_actor_movie_ids(person_id) #get actor's movie ids
    for actor_movie_id in actor_movie_ids:
        actor_movie_cast_ele= tmdb_api_utils.get_movie_cast(movie_id = actor_movie_id, limit=3)
        for ele in actor_movie_cast_ele:
            actor_movie_cast_members.append((ele['id'], ele['name']))
    return actor_movie_cast_members
#get_top3_coactors(2975)    
#get_top3_coactors(6384)

#combine the two functions above:
def get_top3_co_actors(person_id: int):
    tmdb_api_utils = TMDBAPIUtils(apiKey)
    actor_movies= tmdb_api_utils.get_movie_credits_for_person(person_id = str(person_id), vote_avg_threshold = 8)
    actor_movie_ids = []
    for person_movie in actor_movies:
        actor_movie_ids.append(person_movie['id'])

    actor_movie_cast_members = [] #top 3 co-actors for each movie that an actor has participated.
    for actor_movie_id in actor_movie_ids:
        actor_movie_cast_ele= tmdb_api_utils.get_movie_cast(movie_id = actor_movie_id, limit=3)
        for ele in actor_movie_cast_ele:
            actor_movie_cast_members.append((ele['id'], ele['name']))
            

    return actor_movie_cast_members

Laurence_coactor_Nancy = get_top3_co_actors("2975")
Laurence_coactor_Nancy
len(Laurence_coactor_Nancy)


# LF_nodes = 

#   |   FOR each movie cast member:
#   |   |   using graph.add_node(), add the movie cast member as a node (keep track of all new nodes added to the graph)
#   |   |   using graph.add_edge(), add an edge between the Laurence Fishburne (actress) node
#   |   |   and each new node (co-actor/co-actress)
#   |   END FOR
#   END FOR
# END BUILD BASE GRAPH

#
# BEGIN LOOP - DO 2 TIMES:
#   IF first iteration of loop:
#   |   nodes = The nodes added in the BUILD BASE GRAPH (this excludes the original node of Laurence Fishburne!)
#   ELSE
#   |    nodes = The nodes added in the previous iteration:
#   ENDIF
#
#   FOR each node in nodes:
#   |  get the movie credits for the actor that have a vote average >= 8.0
#   |
#   |   FOR each movie credit:
#   |   |   try to get the 3 movie cast members having an 'order' value between 0-2
#   |   |
#   |   |   FOR each movie cast member:
#   |   |   |   IF the node doesn't already exist:
#   |   |   |   |    add the node to the graph (track all new nodes added to the graph)
#   |   |   |   ENDIF
#   |   |   |
#   |   |   |   IF the edge does not exist:
#   |   |   |   |   add an edge between the node (actor) and the new node (co-actor/co-actress)
#   |   |   |   ENDIF
#   |   |   END FOR
#   |   END FOR
#   END FOR
# END LOOP
#
# Your graph should not have any duplicate edges or nodes
# Write out your finished graph as a nodes file and an edges file using:
#   graph.write_edges_file()
#   graph.write_nodes_file()
#
# END BUILD CO-ACTOR NETWORK
# ----------------------------------------------------------------------------------------------------------------------

# Exception handling and best practices
# - You should use the param 'language=en-US' in all API calls to avoid encoding issues when writing data to file.
# - If the actor name has a comma char ',' it should be removed to prevent extra columns from being inserted into the .csv file
# - Some movie_credits may actually be collections and do not return cast data. Handle this situation by skipping these instances.
# - While The TMDb API does not have a rate-limiting scheme in place, consider that making hundreds / thousands of calls
#   can occasionally result in timeout errors. If you continue to experience 'ConnectionRefusedError : [Errno 61] Connection refused',
#   - wait a while and then try again.  It may be necessary to insert periodic sleeps when you are building your graph.


def return_name()->str:
    """
    Return a string containing your GT Username
    e.g., gburdell3
    Do not return your 9 digit GTId
    """
    return "szhao343"


def return_argo_lite_snapshot()->str:
    """
    Return the shared URL of your published graph in Argo-Lite
    """
    
    return "https://poloclub.github.io/argo-graph-lite/#34b97e7e-34a1-4490-9676-773963f1dfa0"


# You should modify __main__ as you see fit to build/test your graph using  the TMDBAPIUtils & Graph classes.
# Some boilerplate/sample code is provided for demonstration. We will not call __main__ during grading.

if __name__ == "__main__":

    graph = Graph()
    person_id = 2975
    person_name = "Laurence Fishburne"

    graph.add_node(id=str(person_id), name=str(person_name))

    actors = get_top3_co_actors(person_id)
    for actor in actors:
        actor_id = actor[0]
        actor_name = actor[1]
        graph.add_node(id = str(actor_id), name = actor_name)
        graph.add_edge(source = str(person_id), target=str(actor_id))
    
        coactors = get_top3_co_actors(actor_id)
        for coactor in coactors:
            coactor_id = coactor[0]
            coactor_name = coactor[1]
            graph.add_node(id = str(coactor_id), name = coactor_name)
            graph.add_edge(source = str(actor_id), target=str(coactor_id))
            coactors2 = get_top3_co_actors(coactor_id)
            for coactor2 in coactors2:
                coactor2_id = coactor2[0]
                coactor2_name = coactor2[1]
                graph.add_node(id = str(coactor2_id), name = coactor2_name)
                graph.add_edge(source = str(coactor_id), target=str(coactor2_id))
    
    graph.write_edges_file(path="edges.csv")
    graph.write_nodes_file(path="nodes.csv")


    # call functions or place code here to build graph (graph building code not graded)
    # Suggestion: code should contain steps outlined above in BUILD CO-ACTOR NETWORK

    # graph.write_edges_file()
    # graph.write_nodes_file()

    # If you have already built & written out your graph, you could read in your nodes & edges files
    # to perform testing on your graph.
    # graph = Graph(with_edges_file="edges.csv", with_nodes_file="nodes.csv")
'''
all_nodes = graph.nodes
all_edges = graph.edges
node_ids = []
for id_person in all_nodes:
    node_ids.append(id_person[0])
#node_ids
nodes_degrees = {node:0 for node in node_ids}
nodes_degrees
for node_id in node_ids:
    for edge in all_edges:
        if node_id in edge:
            nodes_degrees[node_id] += 1
        
nodes_degrees 
#calculate how many keys have values >1
len({k:v for k,v in nodes_degrees.items() if v >1}) #325
'''