#!/usr/bin/env python3
"""
CTF Flag Validator and Scoring System
для Operation Shoulder Takeover
"""

import json
import hashlib
import hmac
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Flag:
    level: int
    content: str
    points: int
    difficulty: str  # easy, medium, hard
    category: str  # auth, ssrf, injection, etc
    dependencies: List[int] = None  # prev flag levels that need to be completed
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

# ============================================================================
# FLAG REGISTRY - Все флаги в CTF
# ============================================================================

FLAGS_DATABASE = [
    # LEVEL 1-5: Reconnaissance & Initial Access
    Flag(
        level=1,
        content="arch_enumeration_completed_gateway_admin_service_found",
        points=10,
        difficulty="easy",
        category="reconnaissance"
    ),
    Flag(
        level=2,
        content="debug_error_messages_exposed_db_version_8_6_detected",
        points=15,
        difficulty="easy",
        category="information_disclosure"
    ),
    Flag(
        level=3,
        content="registered_fake_user_token_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        points=20,
        difficulty="easy",
        category="authentication_bypass",
        dependencies=[1]
    ),
    Flag(
        level=4,
        content="admin_profile_accessed_email_admin@s2s_sports.local",
        points=25,
        difficulty="medium",
        category="idor",
        dependencies=[3]
    ),
    Flag(
        level=5,
        content="admin_user_enumerated_admin_email_exists_in_system",
        points=15,
        difficulty="easy",
        category="information_disclosure",
        dependencies=[3]
    ),
    
    # LEVEL 6-10: Advanced Exploitation
    Flag(
        level=6,
        content="path_traversal_admin_photo_accessed_contained_bank_account",
        points=30,
        difficulty="medium",
        category="path_traversal",
        dependencies=[3]
    ),
    Flag(
        level=7,
        content="nats_message_spoofed_admin_token_created_without_validation",
        points=35,
        difficulty="hard",
        category="ssrf",
        dependencies=[4]
    ),
    Flag(
        level=8,
        content="jwt_token_signed_with_none_algorithm_role_changed_to_superuser",
        points=40,
        difficulty="hard",
        category="jwt_manipulation",
        dependencies=[3]
    ),
    Flag(
        level=9,
        content="race_condition_exploited_event_overloaded_by_2_extra_users",
        points=35,
        difficulty="hard",
        category="race_condition",
        dependencies=[3]
    ),
    Flag(
        level=10,
        content="admin_user_list_exported_found_secret_admin_account_and_password_hash",
        points=40,
        difficulty="hard",
        category="privilege_escalation",
        dependencies=[8, 7]  # Requires superuser access
    ),
    
    # LEVEL 11-15: Deep Exploitation
    Flag(
        level=11,
        content="event_modified_entry_fee_increased_from_0_to_10000_rubles",
        points=35,
        difficulty="medium",
        category="business_logic",
        dependencies=[8, 7]
    ),
    Flag(
        level=12,
        content="anonymous_event_participants_identified_through_photo_metadata_and_timestamps",
        points=30,
        difficulty="medium",
        category="privacy_breach",
        dependencies=[3]
    ),
    Flag(
        level=13,
        content="badge_admin_award_injected_through_nats_user_rating_spoofed",
        points=40,
        difficulty="hard",
        category="message_injection",
        dependencies=[7]
    ),
    Flag(
        level=14,
        content="sql_injection_in_spatial_query_database_error_revealed_admin_table_names",
        points=45,
        difficulty="hard",
        category="sql_injection",
        dependencies=[3]
    ),
    Flag(
        level=15,
        content="ssti_in_email_template_command_execution_confirmed_whoami_output_uid=0",
        points=50,
        difficulty="hard",
        category="ssti",
        dependencies=[3]
    ),
    
    # LEVEL 16-20: System Compromise
    Flag(
        level=16,
        content="pickle_deserialization_rce_achieved_reverse_shell_established",
        points=50,
        difficulty="hard",
        category="deserialization",
        dependencies=[3]
    ),
    Flag(
        level=17,
        content="database_backup_exposed_credentials_admin_password_found_in_sql_dump",
        points=45,
        difficulty="medium",
        category="exposed_credentials",
        dependencies=[6]
    ),
    Flag(
        level=18,
        content="internal_service_admin_api_accessed_without_authentication_inside_docker_network",
        points=40,
        difficulty="hard",
        category="lateral_movement",
        dependencies=[10]
    ),
    Flag(
        level=19,
        content="reflected_xss_executed_user_cookies_and_tokens_exfiltrated",
        points=35,
        difficulty="medium",
        category="xss",
        dependencies=[3]
    ),
    Flag(
        level=20,
        content="complete_system_compromise_audit_logs_cleared_backdoor_installed_on_admin_db",
        points=100,
        difficulty="hard",
        category="full_compromise",
        dependencies=[10, 17, 18]  # All major phases
    ),
]

# ============================================================================
# VALIDATOR SYSTEM
# ============================================================================

class FlagValidator:
    """Validate flag submissions and manage scoring"""
    
    def __init__(self):
        self.submitted_flags: Dict[str, Tuple[Flag, datetime]] = {}
        self.total_score = 0
        self.solved_levels = set()
        
    def validate_flag(self, flag_submission: str) -> Tuple[bool, str, int]:
        """
        Validate flag submission
        Returns: (is_valid, message, points_gained)
        """
        # Extract flag content from format FLAG{...}
        if not flag_submission.startswith("FLAG{") or not flag_submission.endswith("}"):
            return False, "Invalid flag format. Expected: FLAG{...}", 0
        
        flag_content = flag_submission[5:-1]  # Remove FLAG{ and }
        
        # Find matching flag in database
        matching_flag = None
        for flag in FLAGS_DATABASE:
            if flag.content == flag_content:
                matching_flag = flag
                break
        
        if not matching_flag:
            return False, "Flag not found in database", 0
        
        # Check if already submitted
        if flag_submission in self.submitted_flags:
            return False, "Flag already submitted", 0
        
        # Check dependencies
        for dep in matching_flag.dependencies:
            if dep not in self.solved_levels:
                return False, f"Dependency not met: Flag level {dep} must be solved first", 0
        
        # Mark as submitted and add points
        self.submitted_flags[flag_submission] = (matching_flag, datetime.now())
        self.solved_levels.add(matching_flag.level)
        self.total_score += matching_flag.points
        
        return True, f"Flag accepted! +{matching_flag.points} points", matching_flag.points
    
    def get_progress(self) -> Dict:
        """Get current progress information"""
        by_category = {}
        for flag_str, (flag, submit_time) in self.submitted_flags.items():
            if flag.category not in by_category:
                by_category[flag.category] = []
            by_category[flag.category].append({
                'level': flag.level,
                'points': flag.points,
                'submitted_at': submit_time.isoformat()
            })
        
        return {
            'total_score': self.total_score,
            'flags_captured': len(self.submitted_flags),
            'levels_solved': sorted(list(self.solved_levels)),
            'by_category': by_category,
            'next_levels': [f.level for f in FLAGS_DATABASE if f.level not in self.solved_levels][:5]
        }
    
    def export_scoreboard(self) -> Dict:
        """Export data for leaderboard"""
        return {
            'timestamp': datetime.now().isoformat(),
            'score': self.total_score,
            'flags': len(self.submitted_flags),
            'progress': self.get_progress()
        }


# ============================================================================
# HINT SYSTEM
# ============================================================================

HINTS_DATABASE = {
    1: [
        {"difficulty": "easy", "text": "Check /health endpoints for all services"},
        {"difficulty": "medium", "text": "Each microservice has its own /health check"},
        {"difficulty": "hard", "text": "Gateway on port 8005, User Service on 8000, Admin Service on 8003"}
    ],
    2: [
        {"difficulty": "easy", "text": "Try accessing an invalid path to trigger errors"},
        {"difficulty": "medium", "text": "Look at verbose error messages in stack traces"},
        {"difficulty": "hard", "text": "Database version is often exposed in SQL errors. Try 'asdf' in a numerical field"}
    ],
    3: [
        {"difficulty": "easy", "text": "POST to /api/v1/auth/register with phone_number, password, email"},
        {"difficulty": "medium", "text": "Phone number doesn't need real SMS verification"},
        {"difficulty": "hard", "text": "Token format: JWT with header.payload.signature structure"}
    ],
    4: [
        {"difficulty": "easy", "text": "Try changing user_id in the URL path"},
        {"difficulty": "medium", "text": "Admin usually has first UUID like 00000000-0000-0000-0000-000000000001"},
        {"difficulty": "hard", "text": "Use /api/v1/users/{uuid} to get public profile"}
    ],
    5: [
        {"difficulty": "easy", "text": "Compare error messages for existing vs non-existing users"},
        {"difficulty": "medium", "text": "POST /api/v1/auth/login with phone_number + password"},
        {"difficulty": "hard", "text": "'User not found' vs 'Invalid password' - different response codes"}
    ],
    6: [
        {"difficulty": "easy", "text": "File path includes owner_id and filename: /media/avatar/{owner_id}/{file_name:path}"},
        {"difficulty": "medium", "text": "Try using ../ to traverse directories"},
        {"difficulty": "hard", "text": "MinIO stores files as 'avatar/{owner_id}/file.ext' - traverse with ../../../"}
    ],
    7: [
        {"difficulty": "easy", "text": "Connect to NATS at localhost:4222"},
        {"difficulty": "medium", "text": "Subscribe to 'auth.validate_token' topic"},
        {"difficulty": "hard", "text": "Send reply with ok=true and role=superuser"}
    ],
    8: [
        {"difficulty": "easy", "text": "Decode JWT using jwt.io"},
        {"difficulty": "medium", "text": "Try changing algorithm to 'none'"},
        {"difficulty": "hard", "text": "Remove signature when algorithm is 'none'"}
    ],
    9: [
        {"difficulty": "easy", "text": "Create event with max_participants=1"},
        {"difficulty": "medium", "text": "Send 3+ simultaneous join requests in parallel"},
        {"difficulty": "hard", "text": "Use Apache JMeter or custom async script for timing attack"}
    ],
    10: [
        {"difficulty": "easy", "text": "Use superuser token to GET /api/v1/admin/users"},
        {"difficulty": "medium", "text": "Response includes email and password_hash fields"},
        {"difficulty": "hard", "text": "Try cracking hashes with john or hashcat"}
    ],
}

def get_hints(level: int, difficulty: str) -> str:
    """Get hint for specific level"""
    level_hints = HINTS_DATABASE.get(level, [])
    for hint_entry in level_hints:
        if hint_entry['difficulty'] == difficulty:
            return hint_entry['text']
    return "No hint available at this difficulty level"


# ============================================================================
# DOCKER SETUP HELPER
# ============================================================================

DOCKER_COMPOSE_PATCHES = {
    "enable_debug_mode": """
# Add to gateway service environment:
DEBUG: "true"
ENVIRONMENT: "development"
""",
    "disable_sms_verification": """
# Comment out in user_service auth routes:
# await send_sms_verification(phone_number)
# require_sms_verification = False
""",
    "weaken_jwt": """
# In .env:
SECRET_KEY=CHANGE_ME_GENERATE_64_RANDOM_CHARS
ALGORITHM=HS256
""",
    "allow_nats_access": """
# In docker-compose.yml, NATS service:
# Remove --auth flag
# Don't require authentication between services
""",
}

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_vulnerability_report(solved_flags: List[int]) -> str:
    """Generate security report based on flags found"""
    
    report = f"""
SECURITY ASSESSMENT REPORT
Generated: {datetime.now().isoformat()}

Vulnerabilities Discovered:
"""
    
    for level in sorted(solved_flags):
        flag = next((f for f in FLAGS_DATABASE if f.level == level), None)
        if flag:
            report += f"\n[{flag.difficulty.upper()}] {flag.category.upper()}\n"
            report += f"  Level: {level}\n"
            report += f"  Points: {flag.points}\n"
    
    total_points = sum(f.points for f in FLAGS_DATABASE if f.level in solved_flags)
    max_points = sum(f.points for f in FLAGS_DATABASE)
    
    report += f"\n\nSUMMARY:\n"
    report += f"Score: {total_points}/{max_points}\n"
    report += f"Completion: {len(solved_flags)}/{len(FLAGS_DATABASE)} ({100*len(solved_flags)/len(FLAGS_DATABASE):.1f}%)\n"
    
    return report


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='CTF Flag Validator')
    parser.add_argument('--validate', help='Validate flag submission')
    parser.add_argument('--hint', type=int, help='Get hint for level')
    parser.add_argument('--hint-level', type=str, choices=['easy', 'medium', 'hard'])
    parser.add_argument('--list-flags', action='store_true', help='List all flags')
    parser.add_argument('--report', help='Show report for file of solved flags')
    
    args = parser.parse_args()
    
    validator = FlagValidator()
    
    if args.list_flags:
        print("\nAVAILABLE FLAGS:\n")
        for flag in FLAGS_DATABASE:
            print(f"Level {flag.level}: [{flag.difficulty.upper()}] {flag.category}")
            print(f"  Points: {flag.points}")
            print(f"  Content: FLAG{{{flag.content}}}")
            if flag.dependencies:
                print(f"  Requires: {flag.dependencies}")
            print()
    
    elif args.validate:
        is_valid, message, points = validator.validate_flag(args.validate)
        print(f"{'✓' if is_valid else '✗'} {message}")
        if is_valid:
            print(f"\nProgress: {json.dumps(validator.get_progress(), indent=2)}")
    
    elif args.hint and args.hint_level:
        hint_text = get_hints(args.hint, args.hint_level)
        print(f"\nHint for Level {args.hint} ({args.hint_level}):\n")
        print(hint_text)
    
    elif args.report:
        with open(args.report, 'r') as f:
            solved = [int(line.strip()) for line in f if line.strip()]
        print(generate_vulnerability_report(solved))


if __name__ == "__main__":
    main()
