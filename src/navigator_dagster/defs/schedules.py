from typing import Union

import dagster as dg


@dg.schedule(cron_schedule="0 0 1 * *", target="adea_pass_programs_website")
def adea_pass_programs_monthly_schedule(
    context: dg.ScheduleEvaluationContext,
) -> Union[dg.RunRequest, dg.SkipReason]:
    """Monthly schedule to run adea_pass_programs_website asset on the 1st of each month at midnight."""
    return dg.RunRequest(
        run_key=f"adea_pass_programs_monthly_{context.scheduled_execution_time.strftime('%Y%m%d')}",
        tags={"schedule": "monthly", "asset": "adea_pass_programs_website"},
    )
