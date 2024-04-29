# OCI Azure Observability

##  Overview

This sample implements a simple architecture for export of OCI Logs, Events and Metrics to Microsoft Azure Cloud.

### Integration Target Service Options

- [Azure Event Hub](README.azure.eventhub.md)
- [Azure Logging Analytics Workspaces](README.azure.workspace.md)

![](./images/architecture.png)


---
# Testing this Integration Pattern in your OCI Tenancy

Here are sample steps to set up OCI for testing of these patterns. The following shows example
IAM configurations that you need to have in place.  These are examples ... the Policies in 
particular should be reviewed by your SecOps teams. 

## Caveat

You are `strongly` advised to consult your SecOps teams **_BEFORE DEPLOYING IN PRODUCTION ENVIRONMENTS._**

We will set up the following:

- IAM
  - Compartment
  - Policies
  - Group
  - Dynamic Group
- Services
  - Fn Application and Function
  - OCI Streams (for OCI Events)
  - Service Connector Hub
  - VCN

## OCI Compartment

_Name: ABC_

Create a compartment to contain the following:

- Virtual Cloud Network
- Application + Function
- Service Connector

## OCI Group

_Name: functions-developers_

Create a user group where we can assign developer related policies.   

## OCI Policies

See [common policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm).

### Developer Policies

Developer can create, deploy and manage Functions and Applications

See [reference](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/commonpolicies.htm#)

    Allow group functions-developers to manage repos in tenancy
    Allow group functions-developers to manage serviceconnectors in tenancy
    Allow group functions-developers to manage logging-family in tenancy
    Allow group functions-developers to manage functions-family in tenancy
    Allow group functions-developers to use cloud-shell in tenancy
    Allow group functions-developers to use virtual-network-family in tenancy
    Allow group functions-developers to read metrics in tenancy

### Service Connector Policies

Service Connector can access Application + Function, Audit Logs

    Allow any-user to manage functions-family in compartment ABC where all {request.principal.type='serviceconnector'}
    Allow any-user to manage logging-family in compartment ABC where all {request.principal.type='serviceconnector'}

# VCN

Functions must be in a VCN to communicate with Azure.  Use the OCI VCN Wizard as the best
way to do this quickly.  

Create your VCN within the _ABC_ compartment.

# Fn Application

Create your Fn Application within the _ABC_ compartment.

Fn Applications serve as collections of Functions.  We have only one function here.
Also, the Fn Application is where you configure your Function with the parameters it
needs to connect with Azure.

# Build and Deploy the Function

We will need to build and deploy a function.  This guide takes you through the process step by step.

[Quick Start guide on OCI Functions](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartguidestop.htm) before proceeding.

# Need Events?   Use Streaming

If you need to export OCI Events to Azure, best practices call for using OCI Streaming as a durable 
store-and-forward mechanism.  Use of an OCI Stream also means your Service Connector is doing 100% of the
integrations work in terms of passing message payloads across to Azure.

# Service Connector

Create your Service Connector within the _ABC_ compartment.

The Service connector allows you to direct logs, events and raw metrics to the Function
for processing.

## References

Please see these references for more details.

### OCI IaaS Data Sources

- [OCI Logging Service](https://docs.oracle.com/en-us/iaas/Content/Logging/Concepts/loggingoverview.htm)
- [OCI Audit Service](https://docs.oracle.com/en-us/iaas/Content/Audit/Concepts/auditoverview.htm)
- [OCI Monitoring Service](https://docs.oracle.com/en-us/iaas/Content/Monitoring/Concepts/monitoringoverview.htm)
- [OCI Events Service](https://docs.oracle.com/en-us/iaas/Content/Events/Concepts/eventsoverview.htm)
- [OCI CloudGuard](https://docs.oracle.com/en-us/iaas/cloud-guard/using/index.htm)

### OCI IaaS Enabling Technologies

- [OCI Service Connector Hub](https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm)
- [OCI Functions Service](https://docs.oracle.com/en-us/iaas/Content/Functions/Concepts/functionsoverview.htm)
- [OCI Streaming Service](https://docs.oracle.com/en-us/iaas/Content/Streaming/Concepts/streamingoverview.htm)
- [OCI DevOps Pipelines](https://docs.oracle.com/en/solutions/build-cicd-pipelines-devops-function/index.html)


## License
Copyright (c) 2014, 2024 Oracle and/or its affiliates
The Universal Permissive License (UPL), Version 1.0
