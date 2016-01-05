#!/usr/bin/python
# encoding: utf-8

search_query3 = {
                   "query" : {
                       "query_string" : {
                            "fields" :["_type"],
                            "query" : "gps_status",
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

# GPS
gps_unique_filter = ["_source.response.sol_timestamp_wk", "_source.response.sol_timestamp_ms"]
gps_csv_filter = ["_source.meta.time", "_source.meta.spire_id", "_source.response.sol_timestamp_wk", "_source.response.sol_timestamp_ms"]
query_gps_valid = {
                   "query" : {
                       "filtered" : {    
                            "filter": {
                                "bool" : {
                                    "must" : [
                                        { "term" : { "_type" : "gps_status" } },
                                        { "term" : { "meta.spire_id.raw" : "lemur-2-chris" } },
                                        { "range" : { "meta.time" : { "gte" : "2015-10-01", "format": "yyyy-MM-dd" } } }
                                    ],
                                          
                                    "must_not" : [
                                        { "term" : { "response.pos_x" : 0.0 } },
                                    ]                                        
                                }
                            }              
                        }
                    },
                    
                    "sort": [
                        { "meta.time" : { "order": "asc" } },
                    ] 
                }

query_gps = {
                   "query" : {
                       "filtered" : {    
                            "filter": {
                                "bool" : {
                                    "must" : [
                                        { "term" : { "_type" : "gps_status" } },
                                        { "term" : { "meta.spire_id.raw" : "lemur-2-chris" } },
                                        { "range" : { "meta.time" : { "gte" : "2015-10-01", "format": "yyyy-MM-dd" } } }
                                    ],
                                          
                                    #"must_not" : [
                                    #    { "term" : { "response.pos_x" : 0.0 } },
                                    #]                                        
                                }
                            }              
                        }
                    },
                    
                    "sort": [
                        { "meta.time" : { "order": "asc" } },
                    ] 
                }
                
# ADACS
adacs_csv_filter = ["_source.meta.time", "_source.meta.spire_id", "_source.response.acs_op_mode_str", "_source.response.angle_to_go_deg",
                "_source.response.eclipse_flag", "_source.response.qbo_hat", "_source.response.omega_b"]
adacs_csv_filter_desc = ["Beacon Time", "Spire ID", "ACS Operation Mode", "Angle-To-Go (commanded QBO vs estimated QBO) In Degrees",
                     "Is In Eclipse?", "Estimated QBO", "Commanded QBO", "Roll Rate Body Frame (deg/s)"]

query_adacs_nadir_sun = {
    "query" : {
        "filtered" : {
            "filter": {
                "bool" : {
                    "must" : [
                        { "term" : { "_type" : "adacs_status_std" } },
                        { "term" : { "meta.spire_id.raw" : "lemur-2-peter" } },
                        #{ "term" : { "response.acs_mode_str.raw" : "NORMAL" } },
                        { "term" : { "response.eclipse_flag" : 0 } },
                        { "term" : { "response.acs_op_mode_str.raw" : "NORMAL" } },
                        #{ "range" : { "response.angle_to_go_deg" : { "lte" : 10.0 } } },
                        { "range" : { "meta.time" : { "gte" : "2015-10-1", "format": "yyyy-MM-dd" } } }
                    ],
                    
                    #"must_not" : [
                    #    { "term" : { "response.acs_mode_str.raw" : "NORMAL" } },
                    #]                   
                }
            }         
        }
    },
    
    "sort": [
        { "meta.time" : { "order": "asc" } },
    ] 
}
                         
query_adacs_not_nadir_sun = {
    "query" : {
        "filtered" : {
            "filter": {
                "bool" : {
                    "must" : [
                        { "term" : { "_type" : "adacs_status_std" } },
                        { "term" : { "meta.spire_id.raw" : "lemur-2-peter" } },
                        #{ "term" : { "response.acs_mode_str.raw" : "NORMAL" } },
                        { "term" : { "response.eclipse_flag" : 0 } },
                        { "term" : { "response.acs_op_mode_str.raw" : "ACQUISITION" } },
                        #{ "range" : { "response.angle_to_go_deg" : { "gte" : 10.0 } } },
                        { "range" : { "meta.time" : { "gte" : "2015-10-1", "format": "yyyy-MM-dd" } } }
                        #{ "range" : { "meta.time" : { "lte" : "2015-11-13", "format": "yyyy-MM-dd" } } }
                    ],               
                }
            }         
        }
    },

    "sort": [
        { "meta.time" : { "order": "asc" } },
    ]    
}
                                 
query_adacs_sun = {
    "query" : {
        "filtered" : {
            "filter": {
                "bool" : {
                    "must" : [
                        { "term" : { "_type" : "adacs_status_std" } },
                        { "term" : { "meta.spire_id.raw" : "lemur-2-peter" } },
                        #{ "term" : { "response.acs_mode_str.raw" : "NORMAL" } },
                        { "term" : { "response.eclipse_flag" : 0 } },
                        { "range" : { "meta.time" : { "gte" : "2015-10-1", "format": "yyyy-MM-dd" } } }
                        #{ "range" : { "meta.time" : { "lte" : "2015-11-13", "format": "yyyy-MM-dd" } } }
                    ],               
                }
            }         
        }
    },

    "sort": [
        { "meta.time" : { "order": "asc" } },
    ]    
}

query_adacs_all = {
    "query" : {
        "filtered" : {
            "filter": {
                "bool" : {
                    "must" : [
                        { "term" : { "_type" : "adacs_status_std" } },
                        { "term" : { "meta.spire_id.raw" : "lemur-2-chris" } },
                        #{ "term" : { "response.acs_mode_str.raw" : "NORMAL" } },
                        #{ "term" : { "response.eclipse_flag" : 0 } },
                        { "range" : { "meta.time" : { "gte" : "2015-10-1", "format": "yyyy-MM-dd" } } }
                        #{ "range" : { "meta.time" : { "lte" : "2015-11-13", "format": "yyyy-MM-dd" } } }
                    ],
                }
            }         
        }
    },

    "sort": [
        { "meta.time" : { "order": "asc" } },
    ]    
}


