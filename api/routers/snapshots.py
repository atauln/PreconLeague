from fastapi import APIRouter
from db import get_snapshot_by_id, get_all_snapshots, create_snapshot
from typing import Any, Dict
