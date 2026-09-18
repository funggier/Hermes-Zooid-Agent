"""Small operator CLI for the minimal CogentNexus kernel.

This remains a module CLI invoked with python -m hermeszooid.cnx until Zooid owns
its final package and launcher identity.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from .store import CogentNexusStore


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _print(value: Any) -> None:
    print(json.dumps(_jsonable(value), indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m hermeszooid.cnx")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="create one project/ticket with ordered steps")
    create.add_argument("--goal", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--objective", required=True)
    create.add_argument("--accept", action="append", default=[])
    create.add_argument("--step", action="append", required=True)
    create.add_argument("--risk", default="unknown")
    create.add_argument("--uncertainty", default="unknown")

    status = sub.add_parser("status")
    status.add_argument("ticket_id")

    recover = sub.add_parser("recover")
    recover.add_argument("ticket_id")

    claim = sub.add_parser("claim")
    claim.add_argument("ticket_id")
    claim.add_argument("--worker", required=True)

    evidence = sub.add_parser("evidence")
    evidence.add_argument("ticket_id")
    evidence.add_argument("step_id")
    evidence.add_argument("--kind", required=True)
    evidence.add_argument("--value", required=True)
    evidence.add_argument("--criterion", type=int)

    complete_step = sub.add_parser("complete-step")
    complete_step.add_argument("step_id")
    complete_step.add_argument("--summary", default="")

    resolve = sub.add_parser("resolve")
    resolve.add_argument("step_id")
    resolve.add_argument("resolution", choices=["completed", "retry", "blocked"])
    resolve.add_argument("--summary", default="")
    resolve.add_argument("--evidence-kind")
    resolve.add_argument("--evidence-value")
    resolve.add_argument("--criterion", type=int)

    complete_ticket = sub.add_parser("complete-ticket")
    complete_ticket.add_argument("ticket_id")
    complete_ticket.add_argument("--summary", default="")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    with CogentNexusStore.open_default() as store:
        if args.command == "create":
            project = store.create_project(args.goal)
            ticket = store.create_ticket(
                project.id,
                title=args.title,
                objective=args.objective,
                acceptance_criteria=args.accept,
                risk=args.risk,
                uncertainty=args.uncertainty,
            )
            steps = [store.add_step(ticket.id, text) for text in args.step]
            _print({"project": project, "ticket": ticket, "steps": steps})
            return 0

        if args.command == "status":
            ticket = store.get_ticket(args.ticket_id)
            _print({
                "ticket": ticket,
                "steps": store.list_steps(ticket.id),
                "evidence": store.list_evidence(ticket.id),
                "checkpoint": store.latest_checkpoint(ticket.id),
            })
            return 0

        if args.command == "recover":
            _print(store.recover_ticket(args.ticket_id))
            return 0

        if args.command == "claim":
            _print(store.claim_next_step(args.ticket_id, worker_id=args.worker))
            return 0

        if args.command == "evidence":
            _print(store.record_evidence(
                args.ticket_id,
                args.step_id,
                kind=args.kind,
                value=args.value,
                criterion_index=args.criterion,
            ))
            return 0

        if args.command == "complete-step":
            _print(store.complete_step(args.step_id, summary=args.summary))
            return 0

        if args.command == "resolve":
            proof = None
            if args.resolution == "completed":
                if not args.evidence_kind or not args.evidence_value:
                    raise SystemExit(
                        "completed resolution requires --evidence-kind and --evidence-value"
                    )
                proof = {
                    "kind": args.evidence_kind,
                    "value": args.evidence_value,
                    "criterion_index": args.criterion,
                }
            _print(store.resolve_interrupted_step(
                args.step_id,
                resolution=args.resolution,
                summary=args.summary,
                evidence=proof,
            ))
            return 0

        if args.command == "complete-ticket":
            _print(store.complete_ticket(args.ticket_id, summary=args.summary))
            return 0

    return 2
