from collections.abc import Callable

from app.schemas.finding import Finding

PolicyRule = Callable[[list[dict]], Finding | None]


def detect_root_login_without_mfa(events: list[dict]) -> Finding | None:
    for event in events:
        if (
            _text(event.get("eventName")) == "consolelogin"
            and _text(_nested(event, "userIdentity", "type")) == "root"
            and _text(_nested(event, "additionalEventData", "MFAUsed")) in {"no", "false"}
        ):
            return Finding(
                rule_id="POL-ROOT-MFA-001",
                title="Root account login without MFA",
                severity="Critical",
                evidence_summary="A root console login succeeded without MFA.",
                affected_asset=_asset(event, default="AWS root account"),
                recommended_action="Investigate the root login and require MFA for root account access.",
                confidence_score=0.98,
            )
    return None


def detect_iam_privilege_escalation(events: list[dict]) -> Finding | None:
    risky_events = {
        "attachuserpolicy",
        "attachrolepolicy",
        "putuserpolicy",
        "putrolepolicy",
        "addusertogroup",
        "createpolicyversion",
        "setdefaultpolicyversion",
    }

    for event in events:
        event_name = _text(event.get("eventName"))
        policy_text = _flatten_text(event.get("requestParameters", {}))
        if event_name in risky_events and any(
            marker in policy_text
            for marker in (
                "administratoraccess",
                '"action":"*"',
                '"resource":"*"',
                "iam:*",
            )
        ):
            return Finding(
                rule_id="POL-IAM-PRIV-001",
                title="Suspicious IAM privilege escalation",
                severity="High",
                evidence_summary="An IAM change granted or attempted to grant broad administrative privileges.",
                affected_asset=_asset(event, default="IAM principal or policy"),
                recommended_action="Review the IAM change, revoke excessive permissions, and rotate affected credentials if needed.",
                confidence_score=0.92,
            )
    return None


def detect_public_s3_bucket(events: list[dict]) -> Finding | None:
    for event in events:
        text = _flatten_text(event)
        has_s3_signal = "s3" in text or "bucket" in text
        has_public_signal = any(
            marker in text
            for marker in (
                "allusers",
                "authenticatedusers",
                '"public":true',
                '"ispublic":true',
                "publicread",
                "public-read",
            )
        )
        if has_s3_signal and has_public_signal:
            return Finding(
                rule_id="POL-S3-PUBLIC-001",
                title="Public S3 bucket exposure",
                severity="High",
                evidence_summary="S3 bucket configuration indicates public access.",
                affected_asset=_asset(event, default="S3 bucket"),
                recommended_action="Block public access, review bucket policy and ACLs, and validate intended exposure.",
                confidence_score=0.9,
            )
    return None


def detect_security_group_open_to_world(events: list[dict]) -> Finding | None:
    for event in events:
        text = _flatten_text(event)
        if "0.0.0.0/0" in text and any(marker in text for marker in ("securitygroup", "security_group", "ingress")):
            return Finding(
                rule_id="POL-SG-OPEN-001",
                title="Security group open to the internet",
                severity="High",
                evidence_summary="A security group ingress rule allows traffic from 0.0.0.0/0.",
                affected_asset=_asset(event, default="Security group"),
                recommended_action="Restrict ingress to trusted CIDR ranges and remove broad public exposure.",
                confidence_score=0.93,
            )
    return None


def detect_critical_cve(events: list[dict]) -> Finding | None:
    for event in events:
        cvss = event.get("cvss") or event.get("cvss_score") or event.get("cvssScore")
        try:
            cvss_score = float(cvss)
        except (TypeError, ValueError):
            continue

        if cvss_score >= 9.0 and "cve-" in _flatten_text(event):
            return Finding(
                rule_id="POL-CVE-CRITICAL-001",
                title="Critical CVE detected",
                severity="Critical",
                evidence_summary=f"A vulnerability finding reports CVSS {cvss_score:.1f}.",
                affected_asset=_asset(event, default="Vulnerable asset"),
                recommended_action="Prioritize remediation, patch the affected asset, or apply compensating controls.",
                confidence_score=0.96,
            )
    return None


def detect_web_attack_followed_by_500(events: list[dict]) -> Finding | None:
    for index, event in enumerate(events):
        if not _is_web_attack(event):
            continue

        source = event.get("source_ip") or event.get("sourceIPAddress") or event.get("client_ip")
        later_events = events[index:]
        for later_event in later_events:
            later_source = later_event.get("source_ip") or later_event.get("sourceIPAddress") or later_event.get("client_ip")
            same_source = source is None or later_source is None or source == later_source
            if same_source and _status_code(later_event) == 500:
                return Finding(
                    rule_id="POL-WEB-500-001",
                    title="Web attack followed by HTTP 500 error",
                    severity="High",
                    evidence_summary="A web attack indicator was followed by a server error response.",
                    affected_asset=_asset(later_event, default="Web application"),
                    recommended_action="Review application logs, inspect the request path, and patch vulnerable handlers.",
                    confidence_score=0.88,
                )
    return None


POLICY_RULES: tuple[PolicyRule, ...] = (
    detect_root_login_without_mfa,
    detect_iam_privilege_escalation,
    detect_public_s3_bucket,
    detect_security_group_open_to_world,
    detect_critical_cve,
    detect_web_attack_followed_by_500,
)


def _nested(event: dict, *keys: str) -> object:
    value: object = event
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _text(value: object) -> str:
    return str(value or "").strip().lower()


def _flatten_text(value: object) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key}:{_flatten_text(item)}" for key, item in value.items()).lower()
    if isinstance(value, list):
        return " ".join(_flatten_text(item) for item in value).lower()
    return str(value or "").replace(" ", "").lower()


def _asset(event: dict, default: str) -> str:
    for key in ("affected_asset", "asset", "resource", "bucket", "bucket_name", "group_id", "host", "url"):
        value = event.get(key)
        if value:
            return str(value)

    request_parameters = event.get("requestParameters")
    if isinstance(request_parameters, dict):
        for key in ("roleName", "userName", "bucketName", "groupId"):
            value = request_parameters.get(key)
            if value:
                return str(value)

    return default


def _is_web_attack(event: dict) -> bool:
    text = _flatten_text(event)
    return any(
        marker in text
        for marker in (
            "sqlinjection",
            "xss",
            "commandinjection",
            "pathtraversal",
            "../",
            "unionselect",
            "<script",
            "attack:true",
        )
    )


def _status_code(event: dict) -> int | None:
    status = event.get("status") or event.get("status_code") or event.get("http_status")
    try:
        return int(status)
    except (TypeError, ValueError):
        return None
