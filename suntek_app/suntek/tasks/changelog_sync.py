import os
import subprocess
from datetime import datetime

import frappe
import pytz


def changelog_sync():
    try:
        current_path = os.getcwd()
        bench_path = os.path.dirname(current_path)
        repo_path = os.path.join(bench_path, "apps", "suntek_app")

        if not os.path.exists(repo_path):
            frappe.log_error(f"Repository path does not exist: {repo_path}", "Changelog Sync")
            return

        git_command = ["git", "log", "--pretty=format:%h|%s|%an|%ai", "-n", "10"]

        try:
            git_log = subprocess.check_output(
                git_command,
                cwd=repo_path,
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            frappe.log_error(f"Git command failed: {str(e)}", "Changelog Sync")
            return

        if not git_log:
            return

        for line in git_log.split("\n"):
            try:
                hash, message, author, date = line.split("|")

                existing_entry = frappe.get_all("Changelog", filters={"commit_hash": hash}, fields=["name"])

                if existing_entry:
                    continue

                try:
                    parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
                    utc_date = parsed_date.astimezone(pytz.UTC)
                    formatted_date = utc_date.strftime("%Y-%m-%d %H:%M:%S")

                    doc = frappe.get_doc(
                        {
                            "doctype": "Changelog",
                            "commit_hash": hash,
                            "commit_message": message[:140] if message else "",
                            "author": author[:140] if author else "",
                            "timestamp": formatted_date,
                        }
                    )

                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()

                except frappe.DuplicateEntryError:
                    continue
                except frappe.ValidationError as ve:
                    frappe.log_error(
                        f"Validation Error for commit {hash}: {str(ve)}",
                        "Changelog Validation Error",
                    )
                    continue

            except Exception as e:
                frappe.log_error(
                    f"Error processing commit {hash if 'hash' in locals() else 'unknown'}: {str(e)}",
                    "Changelog Entry Error",
                )
                continue

    except Exception as e:
        frappe.log_error(f"Changelog Sync Failed: {str(e)}", "Changelog Sync Error")
        raise
