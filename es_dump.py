#!/usr/bin/python
# encoding: utf-8

import warnings
import base64
#from urllib3.exceptions import InsecureRequestWarning
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import json
import optparse

# Handle option parsing
opt_parser = optparse.OptionParser()
opt_parser.add_option('-n', '--name', dest='name', help='Login name', 
                      metavar='NAME', default='spire')
opt_parser.add_option('-p', '--pwd', dest='pwd', help='Login password', 
                      metavar='PWD', default='')

(opt_args, args) = opt_parser.parse_args()

ES_USER = opt_args.name
ES_PASSWD = opt_args.pwd
ES_URL = 'https://{}:{}@truffula.pvt.spire.com/elasticsearch'.format(ES_USER, ES_PASSWD)

es = Elasticsearch([ES_URL])
print(es)

search_query2 = {
                   "query" : {
                       "query_string" : {
                            "_type" : {
                                "query" : "gps_status",
                            },
                        },
                   },
                }

search_query3 = {
                   "query" : {
                       "query_string" : {
                            "fields" :["_type"],
                            "query" : "gps_status",
                        },
                   },
                }

search_query4 = {
                   "query" : {
                       "match" : {
                            "fields" :["_type"],
                            "query" : "gps_status",
                        },
                   },
                }

search_query5 = {
                   "query" : {
                       "bool" : {
                            "must" : {
                                "term" : {
                                    "_type" : "gps_status"
                                }
                            },
                        },
                   },
                }

search_query6 = {
                   "query" : {
                       "filtered" : {
                           "query" : {
                                "query_string" : {
                                    "fields" :["_type"],
                                    "query" : "gps*",
                                }
                            },
    
                            "filter": {
                                "bool" : {
                                    "must" : [{ "term" : { "_type" : "gps_status" } }]
                                },
                            },
                        },
                    },
                }

search_query7 = {
                    "query" : {
                        "constant_score" : {
                            "filter": {
                                "term":  { 
                                    "_type": "gps_status" 
                                },
                            
                            },
                        },
                    },
                }

search_query8 = {
                   "query" : {
                       "filtered" : {
                            "filter": {
                                "bool" : {
                                    "must" : #[#{ "term" : { "_type" : "gps_status" } },
                                              { "term" : { "meta.spire_id" : "lemur-2-joel" } }
                                            # ]
                                },
                            },
                        },
                    },
                }

search_query9 = {
                   "query" : {
                       "filtered" : {
                           "query" : {
                                "term" : {
                                    #"fields" :["meta.spire_id"],
                                    "meta.spire_id" : "lemur-2-joel"
                                }
                            },
    
                            "filter": [ {
                                "bool" : {
                                    "must" : [{ "term" : { "_type" : "gps_status" } }]
                                }},
                                
                                {       
                                "range" : {
                                    "meta.time" : {
                                        "gte" : "2015-11-30",
                                        "format": "yyyy-MM-dd"                                        
                                    },
                                }}
                            ],
                        },
                    },
                }

search_query10 = {
                   "query" : {
                       "filtered" : {
                           "query" : {
                                "query_string" : {
                                    "fields" :["_type"],
                                    "query" : "gps*",
                                }
                            },
    
                            "filter": [ {
                                "bool" : {
                                    "must" : [{ "term" : { "meta.time" : "2015-11-25T09:11:49" } }]
                                }},
                            ],
                        },
                    },
                }

search_query11 = {
                   "query" : {
                       "query_string" : {
                            "fields" :["meta.time"],
                            "query" : "*",
                        },
                   },
                }


search_query = {
                   "query" : {
                       "filtered" : {    
                            "filter": {
                                "bool" : {
                                    "must" : [
                                        { 
                                            "term" : { "_type" : "gps_status" } 
                                        },
                                        {
                                            "term" : { "meta.spire_id.raw" : "lemur-2-chris" } 
                                        },
                                        {       
                                            "range" : {
                                                "meta.time" : {
                                                    "gte" : "2015-11-30",
                                                    "format": "yyyy-MM-dd"                                        
                                                }
                                            }
                                        }
                                    ],
                                          
                                    "must_not" : [
                                        {
                                            "term" : { "response.pos_x" : 0.0 }
                                        },
                                    ]                                        
                                }
                            }              
                        }
                    }
                }

search_query12 = {
                   "query" : {
                       "term" : {
                            "meta.spire_id.raw" : "lemur-2-joel"
                        },
                   },
                }

matches = es.search(index="spire", body=search_query, size=300)
hits = matches['hits']['hits']
print(json.dumps(matches, indent=4, separators=(',', ':')))
#print(json.dumps(hits, indent=4, separators=(',', ':')))
