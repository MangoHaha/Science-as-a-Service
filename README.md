# Science-as-a-Service

Cumulus Laboratories
David Kuhta
Feng Gao

To run locally

    python cumulus.py

		Go to http://localhost:8111 in your browser


Our application is a Science-as-a-Service platform for customers to order automated test experiments and for administrators to manage their laboratory equipment. The managerial portion of the database will be centered around a laboratory, its equipment and respective functionality. The customer focus will be ordering a protocol, an experiment composed of a set of instructions, denoting a sequence of operations to be enacted on a given sample by the equipment in a specified lab, and
reviewing results. The instructions will identify a function (ex: incubate, seal, transfer, spectrophotometry) and the table for that function will store detailed parameters for its type (ie. duration for incubating vs volume for transfer fluid). Customers will select from a list of predetermined protocols, but will be able to modify the aforementioned parameters for a given instruction (with certain factors limited by the admin based on equipment features). For example, an instruction
might specify heating a sample and the customer could specify temperature and duration. The application code will generate “random” results by transforming a standard dataset using the customer’s supplied parameters. Administrators will be able to perform all the standard CRUD operations on the laboratory and equipment in addition to their activation status, thereby constraining which laboratory can process an order.  Equipment and laboratories attributes will derive from existing
commercial cloud labs in conjunction with internet searches for a given category of equipment. The largest challenges will stem from automated database updates (processing & scheduling orders and assigning laboratories) as well as building the relationship between instruction sets and their corollary sub-typed function tables.
