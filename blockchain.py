import hashlib
import datetime

def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

def create_block(voter_id, candidate_id, previous_hash):
    timestamp = str(datetime.datetime.now())

    block_data = f"{voter_id}{candidate_id}{timestamp}{previous_hash}"
    current_hash = generate_hash(block_data)

    return {
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
        "current_hash": current_hash
    }
