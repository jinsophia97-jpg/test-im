"""Internal employee and IT service-desk demo logic.

The functions are intentionally plain Python so the SSO frontend publish path
does not pull in the full veADK / model dependency stack during image build.
"""

from itertools import count

# --- Mock backends (replace with your real systems) --------------------------

# Internal IT / HR knowledge base: topic -> answer.
_KNOWLEDGE_BASE = {
    "vpn": "连接 VPN:安装 GlobalProtect,门户填 vpn.corp.example.com,用工域账号 + 动态口令登录。",
    "报销": "报销流程:在「财务系统 > 我的报销」上传发票并选择项目,主管审批后约 3 个工作日到账。",
    "设备申领": "设备申领:在「IT 服务台 > 设备申领」提交申请并选择机型,主管审批后到前台领取。",
    "密码重置": "密码重置:访问 sso.corp.example.com/reset,通过手机验证码重置;连续锁定 3 次请提工单。",
    "权限": "系统权限:在「IT 服务台 > 权限申请」选择目标系统与角色,由数据 Owner 审批后生效。",
}

# Support tickets created in this process: id -> record.
_TICKETS: dict[str, dict] = {}
_ticket_seq = count(1001)

# Remaining annual-leave balance (days) by employee id.
_LEAVE_BALANCE = {"e1001": 8.5, "e1002": 12.0, "e2043": 3.0}


# --- Tools -------------------------------------------------------------------

def search_knowledge_base(query: str) -> dict:
    """Search the internal IT/HR knowledge base for how-to guides and policies.

    Args:
        query: What the employee is asking about, e.g. "VPN", "报销", "密码重置".

    Returns:
        A dict with the best-matching "article", or a miss message.
    """
    q = query.lower().strip()
    for topic, article in _KNOWLEDGE_BASE.items():
        if topic in q or q in topic:
            return {"topic": topic, "article": article}
    return {"article": f"知识库未命中「{query}」,建议创建工单交由 IT 人工跟进。"}


def create_support_ticket(subject: str, category: str = "IT", urgency: str = "normal") -> dict:
    """Create an internal support ticket on behalf of the employee.

    Args:
        subject: Short description of the issue.
        category: Ticket category, e.g. "IT", "HR", "Facilities".
        urgency: Priority — one of "low", "normal", "high".

    Returns:
        A dict with the new ticket id and its initial status.
    """
    ticket_id = f"INC-{next(_ticket_seq)}"
    _TICKETS[ticket_id] = {"subject": subject, "category": category, "urgency": urgency, "status": "open"}
    return {"ticket_id": ticket_id, "status": "open", "message": f"已创建工单 {ticket_id}({category}/{urgency})。"}


def get_ticket_status(ticket_id: str) -> dict:
    """Look up the current status of a previously created support ticket.

    Args:
        ticket_id: The ticket id, e.g. "INC-1001".

    Returns:
        A dict with the ticket's status and details, or a not-found message.
    """
    ticket = _TICKETS.get(ticket_id.upper().strip())
    if not ticket:
        return {"result": f"未找到工单 {ticket_id}。"}
    return {"ticket_id": ticket_id.upper().strip(), **ticket}


def check_leave_balance(employee_id: str) -> dict:
    """Check an employee's remaining annual-leave balance, in days.

    Args:
        employee_id: The employee id, e.g. "e1001".

    Returns:
        A dict with the remaining leave days, or a not-found message.
    """
    days = _LEAVE_BALANCE.get(employee_id.lower().strip())
    if days is None:
        return {"result": f"未找到员工 {employee_id} 的假期信息。"}
    return {"employee_id": employee_id.lower().strip(), "annual_leave_days": days}


def handle_message(message: str) -> str:
    """Return a deterministic demo response for the frontend SSO flow."""
    text = (message or "").strip()
    lower = text.lower()

    if not text:
        return (
            "你好,我是企业内部员工助手。你可以问我 VPN、报销、设备申领、"
            "密码重置、权限、工单或年假余额。"
        )

    if "年假" in text or "leave" in lower:
        employee_id = _find_employee_id(lower)
        if not employee_id:
            return "请告诉我你的员工 ID,例如 e1001,我就可以查询年假余额。"
        result = check_leave_balance(employee_id)
        days = result.get("annual_leave_days")
        if days is None:
            return result["result"]
        return f"{employee_id} 当前剩余年假为 {days} 天。"

    ticket_id = _find_ticket_id(text)
    if ticket_id:
        result = get_ticket_status(ticket_id)
        if "result" in result:
            return result["result"]
        return f"{ticket_id} 当前状态是 {result['status']},主题:{result['subject']}。"

    if "工单" in text and any(word in text for word in ("创建", "新建", "提交", "开")):
        result = create_support_ticket(subject=text, category="IT", urgency="normal")
        return result["message"]

    for topic in _KNOWLEDGE_BASE:
        if topic in lower or topic in text:
            return search_knowledge_base(topic)["article"]

    return (
        "我可以协助处理 IT/HR 常见问题:VPN、报销、设备申领、密码重置、"
        "权限申请、工单创建/查询、年假余额查询。请告诉我你想办理什么。"
    )


def _find_employee_id(text: str) -> str | None:
    for employee_id in _LEAVE_BALANCE:
        if employee_id in text:
            return employee_id
    return None


def _find_ticket_id(text: str) -> str | None:
    for part in text.replace(",", " ").replace("，", " ").split():
        candidate = part.upper().strip("。.!?？")
        if candidate.startswith("INC-"):
            return candidate
    return None
