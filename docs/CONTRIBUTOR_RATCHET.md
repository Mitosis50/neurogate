# Contributor Ratchet — 24h Response Protocol

## The rule (Jev parameter #7)
Every PR/issue gets a PUBLIC response within 24 hours. No exceptions. The response is one of:
1. **Merged** (if green CI + scope match)
2. **Review started** (specific feedback, named reviewer)
3. **Blocked with reason** (CI failure, scope mismatch — say exactly what would unblock)
4. **Held** (needs council decision — say so and open the council thread)

## Fleet-assisted triage (the differentiator)
- AI fleet (Mira + Jev-shadow) drafts the first response + labels + test notes within minutes.
- A human maintainer confirms within 24h. **The AI never merges alone** (V-gate principle:
  AI pre-screens, human decides).
- Every AI-drafted response is labeled `assist:ai-drafted` in the thread. Radical transparency.

## Metrics (Jev #9)
- downstream_usage (integrations/adoption) > stars
- contributor conversion = PRs from first-time contributors / forks
- median time-to-first-response (target: < 4h fleet draft, < 24h human confirm)
