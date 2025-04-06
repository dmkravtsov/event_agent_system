# Event Aggregator System

## Description

Event Aggregator System is a multi-agent platform designed to collect, process, and store event information from various APIs such as Ticketmaster and SerpApi. It supports natural language queries, asynchronous data fetching, deduplication, structured logging, and integration with Firebase Firestore.

## Features

- Natural language query interpretation
- Asynchronous multi-agent architecture
- Ticketmaster and SerpApi integration
- Event deduplication by title, venue, and date
- Logging of events and duplicates
- Export to local JSON files
- Firebase Firestore storage support

## Configuration

The system uses a `config.yaml` file for managing API keys, default values, and feature toggles. Firebase service account credentials must be provided in JSON format and referenced in the configuration.

## Logging and Storage

All retrieved and deduplicated events are saved to `results.json` and `logs/events.log`. Duplicate entries are recorded separately in `logs/duplicates.log`. Firebase Firestore is used to persist final event data in the cloud.
