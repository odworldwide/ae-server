import tracery
from tracery.modifiers import base_english

weather_obj = {
   "origin":[
      "#intensity# #weatherType# #preposition# #place#, #verb2# #preposition2# #amount# of #quality#. #advice##endpunctuation#",
      "The #water# #verb3# #adjective#. #advice#."
   ],
   
   "intensity":[
      "Sharp",
      "Pre-ordained",
      "Spirited",
      "Lethargic",
      "Listless",
      "Unstable",
      "Bright",
      "Certain",
      "Strong",
      "Energetic",
      "Weak",
      "Pale",
      "Soft",
      "Understated",
      "Dominant",
      "Aggressive",
      "Attacking",
      "Powerful",
      "Authoritative",
      "Conservative",
      "Shrewd",
      "Disciplined",
      "Offensive",
      "Trespassing",
      "Encroaching",
      "Invading",
      "Resistant",
      "Resilient"
   ],
   
   "direction":[
      "south-westerly",
      "northerly",
      "southerly",
      "western",
      "eastern",
      "northerly",
      "north-easterly"
   ],
   
   "weatherType":[
      "winds",
      "gusts",
      "gales",
      "air",
      "storm",
      "depression",
      "cyclonic depression",
      "hurricane force"
   ],
   
   "verb":[
      "backing",
      "feeding",
      "gaining strength",
      "losing strength",
      "weakening",
      "loosening its grip",
      "travelling",
      "dissipating",
      "gaining ground",
      "growing stronger",
      "losing faith",
      "losing energy",
      "focusing",
      "rushing",
      "veering",
      "gaining its identity",
      "losing its identity",
      "in formation"
   ],
   "preposition":[
      "into",
      "over",
      "across"
   ],
   "place":[
      "the Sargasso Sea",
      "the Gulf of Mexico",
      "the Argentine Sea",
      "the Carribean Sea",
      "the Gulf of Guinea",
      "the Gulf of Bothnia",
      "the mid-Atlantic Ridge",
      "the Denmark Strait",
      "the Straits of Florida",
      "the Gulf of Maine",
      "the Gulf of Saint Lawrence",
      "the Gulf of Finland",
      "the Foxe Basin",
      "the Bay of Mexico",
      "the Gulf of Florida",
      "the bay of Campeche"
   ],

   "verb2":[
      "breaking",
      "drifting",
      "falling",
      "travelling",
      "collapsing",
      "shooting",
      "driving",
      "cruising",
      "flowing"
   ],

   "preposition2":[
      "between",
      "through",
      "over",
      "past"
   ],

   "amount":[
      "spells",
      "recesses",
      "moments",
      "surges",
      "bouts"
   ],

   "quality":[
      "intensity",
      "coldness",
      "danger",
      "hope",
      "uncertainty",
      "longing",
      "yearning",
      "desire",
      "fear",
      "outrage",
      "melancholy",
      "grief",
      "anxiety",
      "arousal",
      "benevolence",
      "peace"
   ],

   "advice":[
      "Watch closely for fluctuations in surface temperature ",
      "A powerful intervention is necessary for a correction",
      "The current prediction must be seen as one element of a much larger system",
      "Uncertainties will surface soon",
      "Danger and opportunity awaits",
      "Beware a tendency toward collapse",
      "No more new orders",
      "Discipline or corrections expected in the near future",
      "A punishing time ahead",
      "Confessions are anticipated",
      "Opportunities abound",
      "Victory is uncertain",
      "Make plans to proceed",
      "Beware the advice of others",
      "Go into retreat",
      "These certainties are in the hands of heaven",
      "Nothing is expected",
      "Maintain caution",
      "The wind is moving against you",
      "Expect general doom and gloom",
      "A wolf in sheep's clothing",
      "Impending disaster",
      "A reversal is in the works",
      "Pay attention",
      "Proceed softly",
      "The arrival of low spirits ahead"
   ],

   "water":[
      "sea",
      "water",
      "ocean",
      "horizon"
   ],

   "verb3":[
      "remains",
      "is",
      "shall be",
      "is becoming",
      "was",
      "are getting",
      "are still",
      "won't stay",
      "will be"
   ],

   "adjective":[
      "smooth",
      "cool again",
      "calm",
      "angry",
      "tense",
      "ambient",
      "passive",
      "serene",
      "dark",
      "docile",
      "restful",
      "tranquil",
      "harder than usual"
   ],

   "endpunctuation":[
      ".",
      "?"
   ]
}

market_obj = {
   "origin":[
      "#what# #marketQuality# #marketObject##timeComment##question#",
      "#futureAction# #if# #futureState#",
   ],

   "what":[
      "quite",
      "such",
      "rather",
      "none the wiser about such",
      "just",
      "who knows about",
      "what",
      "it's just",
      "just such",
      "it's still quite",
      "wow ",
      "damn,",
      "oof ",
      "fuck,",
      "god,"
   ],

   "marketQuality":[
      "a volatile",
      "an unpredictable",
      "an unforeseeable",
      "a dubious",
      "a random",
      "an uncertain",
      "an unusual",
      "a changeable",
      "a variable",
      "an inconstant",
      "an inconsistent",
      "an uncertain",
      "an erratic",
      "an irregular",
      "an unstable",
      "a turbulent",
      "an unsteady",
      "an unsettled",
      "an unreliable",
      "an undependable",
      "a varying",
      "a shifting",
      "a fluctuating",
      "a fluid",
      "wavering",
      "an impulsive",
      "a wayward",
      "a temperamental",
      "a wild",
      "an opportune",
      "a tasty"
   ],

   "marketObject":[
      "market",
      "bond",
      "price",
      "track",
      "value",
      "yield",
      "ROI",
      "rate of return",
      "loss ratio",
      "VaR",
      "risk"
   ],

   "timeComment":[
      " so far",
      " today",
      " atm",
      " now",
      " these days",
      " this week",
      " lately",
      " recently",
      " now",
      "",
      "",
      "",
      "",
      "",
      ""
   ],

   "question":[
      ", no?",
      ", isn't it?",
      ", it's true",
      "",
      ""
   ],

   "futureAction":[
      "I'll buy in",
      "i'm selling",
      "it's still good pickings",
      "better get in there",
      "you should all fill up",
      "get your orders in",
      "should bid",
      "numbers are good",
      "fill up early",
      "buy buy",
      "BUY HIGH",
      "sell higher than you think"
   ],

   "if":[
      "today",
      "when",
      "if",
      "now",
      "since",
      "as long as",
      "so long as",
      "whenever",
      "while"
   ],

   "futureState":[
      "the markets are slow",
      "the price is low",
      "the seas stay quiet",
      "everyone's sitting on their hands still",
      "the premiums are still good",
      "the stocks are staying this quiet",
      "the pandemic is still in full swing"
   ]
}

def market():
	grammar = tracery.Grammar(market_obj)
	grammar.add_modifiers(base_english)
	response = grammar.flatten("#origin#")
	# print(response)
	return response

def weather():
	grammar = tracery.Grammar(weather_obj)
	grammar.add_modifiers(base_english)
	response = grammar.flatten("#origin#")
	# print(response)
	return response
