#!/bin/bash

pkill -f uvicorn || true
pkill -f "npm run dev" || true
pkill -f vite || true