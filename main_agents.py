from agent import agent_router

#x = agent_router.process('Conversation started')
#print (x)
#x = agent_router.process('I am an avid biker. I always want to bike when possible. So please consider all further requests with that in mind.')
#print (x)
x = agent_router.process('I wish to go from a stop in London with the code 490000119F to a stop with the code 490000040A on 11th November departing at six in the evening. I am the most interested in biking routes. Please show me the route on a map as well.')
print (x)
x = agent_router.process('Thanks for the map. I wonder if you could give me a step by step description of the journey as well, like streets to bike down, where to turn and the like?')
print (x)
x = agent_router.process('Tremendous. But I just realized there will be rain (London, not the sunniest of places). So could you give me a route with the tube as well. Create map as well as step by step description please.')
print (x)
