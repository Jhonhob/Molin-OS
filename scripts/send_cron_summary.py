#!/usr/bin/env python3
"""
墨麟OS Cron任务Bot摘要发送器
在每个cron job执行完毕后调用，用对应Bot的身份发送执行摘要给创始人

Usage: python3 send_cron_summary.py <profile_name> <job_name> <status> [summary]
profile_name: ziling | yuanyao | yinyue | meining | songyu | xuanhu
"""

import sys, json, requests, os

# ===== 所有Bot凭据（从domain YAML配置读取） =====
BOTS = {
    "ziling": {
        "app_id": "cli_aa8967ade53cdbc3",
        "app_secret": "xRYaDk59r9S4IuNP8jpgUhMYbrkOV7IJ",
        "name": "紫灵"
    },
    "yuanyao": {
        "app_id": "cli_a956c83187395cd4",
        "app_secret": "BNoCjgLp6SqdnojTE0BxofA2fyExEpPI",
        "name": "元瑶"
    },
    "yinyue": {
        "app_id": "cli_a966ede1d9789bd2",
        "app_secret": "6dHUcHxEo98AfORMBGy5lgTVxnLgjDHm",
        "name": "银月"
    },
    "meining": {
        "app_id": "cli_aa881c316d789bb5",
        "app_secret": "fauTnJwa1hGaqncFmOAnThxg2MBHCgSM",
        "name": "梅凝"
    },
    "songyu": {
        "app_id": "cli_a9513691d4f89bcf",
        "app_secret": "S9eVOrjLArN710E3S497Ph4hWCmECOu4",
        "name": "宋玉"
    },
    "xuanhu": {
        "app_id": "cli_aa884b4a88bc9bb4",
        "app_secret": "yjioEHla8DmwQtzyOMvg0b8xVnXn4vFh",
        "name": "玄骨"
    }
}

# ===== 创始人尹建业在每个Bot应用下的 Open ID =====
USER_OPEN_IDS = {
    "ziling": "ou_4a7dbb113596833a9cbbe5f799e15554",
    "yuanyao": "ou_1c4ee0a310a4383eceffedfc59b03100",
    "yinyue": "ou_5b28c03558c82e5da78ea593d02a0a81",
    "meining": "ou_0322d06df3d36d71c84af8837256d4e2",
    "songyu": "ou_7a93ff2be01c924a89c2ee008508c350",
    "xuanhu": "ou_c0ef354c961528e83502d4286978ceb5"
}

def send_dm(profile_name, job_name, status, summary=""):
    """用指定Bot的身份发送直接消息给创始人"""
    bot = BOTS.get(profile_name)
    if not bot:
        print(f"❌ 未知profile: {profile_name}")
        return False

    user_open_id = USER_OPEN_IDS.get(profile_name)
    if not user_open_id:
        print(f"❌ 未知profile: {profile_name}")
        return False

    # Get token
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": bot["app_id"], "app_secret": bot["app_secret"]},
        timeout=30
    )
    token_data = r.json()
    token = token_data.get("tenant_access_token")
    if not token:
        print(f"❌ {bot['name']} token获取失败: {token_data.get('msg','')}")
        return False

    # Build message
    emoji = "✅" if "ok" in status.lower() or status == "ok" else "❌"
    msg_text = f"""🤖 {bot['name']} · 定时任务报告

{emoji} {job_name}
状态: {status}"""
    if summary:
        msg_text += f"\n\n{summary[:400]}"

    # Send DM to user
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "receive_id": user_open_id,
        "msg_type": "text",
        "content": json.dumps({"text": msg_text})
    }
    
    r2 = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        json=payload, headers=headers, timeout=30
    )
    result = r2.json()
    if result.get("code") == 0:
        print(f"✅ {bot['name']} → 已发送到创始人对话框")
        return True
    else:
        print(f"❌ {bot['name']} 发送失败: {result.get('msg','')}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: send_cron_summary.py <profile> <job_name> <status> [summary]")
        print("  profile: ziling | yuanyao | yinyue | meining | songyu | xuanhu")
        sys.exit(1)
    
    profile = sys.argv[1]
    job_name = sys.argv[2]
    status = sys.argv[3]
    summary = sys.argv[4] if len(sys.argv) > 4 else ""
    
    send_dm(profile, job_name, status, summary)
