# Building a new scanning task

A scanning task is made up of a number of components, these are described below.

Common across all Python directories is the need to have a `__init__.py` directory which is used by pipenv

INSERT DIAGRAM SHOWING FLOW THROUGHOUT THIS PROCESS

## Triggering the task

Your task would usually be triggered by an SNS event. In the `sns_listener` directory is a listener that listens for an event, usually from the output of the nmap primary scanner, and if certain conditions are met adds an event to an SQS queue to start a secondary task.

## Task Queue Consumer

In the `task_queue_consumer` directory is an SQS listener that listens for events for this task.

In here you would typically validate the input, and return an error if the input doesn't match the conditions for the task.

Once you have performed validation, you would then trigger the task.

For a Lambda task, this is straightforward and can just be another function in the Task Queue Consumer.

For an ECS/Fargate task, this will set up the parameters to initiate the task, and send this to ECS.

The parameters passed to this via the queue are useful later on, and these are passed to the task as an object, which is stored alongside the S3 file as metadata.

Note that for a Lambda task, you might need to extend the execution time (up to 15 minutes at the time of writing) - you can set this in `task_queue_consumer.tf` using the `timeout` parameter.  The default Lambda timeout is 3 seconds if this is not specified, and may not be a sufficient length of time for a task that is network bound.

## Parsing results

In the `results_parser` directory there is a python file for a Lambda function which is triggered when there is a new file in the S3 bucket.

Once you've extracted the file, you would parse the data to extract all the data that is relevant to the scan before sending this to Elastic.

The files remain in S3 so that in future the data could be re-ingested, for example if we want to extract other data from the files that wasn't in the original scan.

## Sending to Elastic

Once you have extracted the data, it is then sent to Elastic.  A `ResultsContext` class is provided to help manage the data that is sent.

First you should set up a `non_temporal_key` which contains your base set of keys to send to Elastic.

Now you can push extra keys to this context with `results_context.push_context` or pop the last set of keys added with `results_context.pop_context`.  To post results to Elastic, use `results_context.post_results`


## Kibana integration

Once you have your data flowing into Kibana, you can build a visualisation.

First you need to set up an index within Kibana, create a search, and then make a visualisation based on this.

When you're happy with what you've created you should copy it into your task into the `elastic_resources` directory:

### Indexes

In the `indexes` directory you will need to manual add any fields that you want to be indexed - there are two files here that are referenced by `indexes.tf`

Within `indexes.tf` the `index_name` value should match the topic name that you use in `results_context.post_results()` in your results parser

### Searches

In the `searches` directory you should make one file for each search that you want to have for the scanning task.

You can export these in Kibana by going to Management -> Saved Objects -> Searches and exporting each search.

Copy the contents of the `"_source"` section into the `"attributes"` section in your `.search.json` file, replacing the `title` value with `"${object_title}"` and within the search, change the `"index"` value to `"${index}"`

The search files are referenced by `searches.tf`

### Visualisations

In the `visualisations` directory you should make one file for each visualisation that you have for the scanning task.

You can export these in Kibana by going to Management -> Saved Objects -> Visualizations and exporting each visualisation.

Copy the contents of the `"_source"` section into the `"attributes"` section in your `.vis.json` file, replacing:
* the `title` value with `"${object_title}"` in all instances
* the `"index"` value to `"${index}"` in all instances
* the `"savedSearchId"` value to `"${search_id}"` in all instances

The search files are referenced by `visualisations.tf`


## Packaging up the Lambdas

All the Lambdas are packaged into one zip - the terraform to make this is in the `ssl_lambdas` directory.  The correct python file is invoked in each Lambda function resource


## Fargate

