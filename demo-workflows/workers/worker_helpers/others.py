import return_logs
import postgresql_worker
from typing import Optional

from util import DbEncryption

CANNOT_GET_DEVICE_CREDENTIALS = {"error": "Cannot get credentials for device from oam domain"}


def get_device_credentials(oam_domain: str) -> Optional[dict]:
    """ Get device credentials from DB based on inputted oam domain"""
    cur, conn = None, None

    try:
        cur, conn = postgresql_worker.open_conn()
        cur.execute("SELECT login,password FROM oam_domain WHERE management_domain=%s", (oam_domain.lower(),))
        credentials = cur.fetchone()

        if not credentials:
            return_logs.error("oam domain '%s' does not exist in db.", oam_domain)
            return
        return {"username": DbEncryption.decrypt(credentials.login),
                "password": DbEncryption.decrypt(credentials.password)}

    except Exception:
        return_logs.exception("Selecting oam domain '%s' from database failed", oam_domain)
        return

    finally:
        postgresql_worker.close_conn(conn)
