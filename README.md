# UDP Live Polling and Voting System

## Overview
This project implements a **network-based live polling system using UDP socket programming in Python**.  
Multiple clients can send votes to a central server, and the server broadcasts live voting results to all connected clients.

The system also performs **statistical packet loss analysis** to evaluate network performance, which is useful since UDP does not guarantee delivery.

---

## Features

- Multi-client voting system
- Real-time result broadcasting
- Duplicate vote detection
- UDP socket communication
- Sequence-number based packet tracking
- Statistical packet loss analysis
- Simulated packet loss for testing

---

## System Architecture
