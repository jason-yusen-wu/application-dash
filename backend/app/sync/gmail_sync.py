def sync_user_mailbox(user_id: int) -> None:
    """Pull new messages since the last synced historyId, classify the
    job-application candidates, and upsert the corresponding applications.

    Intentionally not implemented — History API polling/pagination, the
    classification pipeline, and state-machine transitions are left to you.
    """
    raise NotImplementedError
