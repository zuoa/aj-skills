from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from test_validate_blueprint import MODULE, build_valid_blueprint, document


DOMAIN = """# Reservation behavior

## SPEC-CORE-001 — Reserve a slot

- Source: PRD-CORE-001
- State: confirmed
- Actors: member
- Trigger: reservation request
- Preconditions: member is signed in
- Inputs: available slot identifier
- Rules: a slot cannot be reserved twice
- Outcome: reservation appears in the member's list

### AC-CORE-001 — Available slot

- Verification: automated
- Fixture: signed-in member and an available slot
- Assertion: exactly one reservation belongs to that member
- Procedure: run the reservation integration test
- Evidence required: integration report and stored reservation
- Result: not-run

- GIVEN an available slot
- WHEN the member reserves it
- THEN one reservation appears in their list
"""
INTERFACE = """# Reservation contract

## IFACE-CORE-001 — Reservation request

- Source: SPEC-CORE-001
- State: confirmed
- Provider: reservation service
- Consumer: member client
- Protocol: JSON Schema
- Contract: [request schema](../../contracts/reservation.json)
- Operations: reservation.create maps to AC-CORE-001
- Auth: authenticated member; server determines ownership
- Errors: unavailable slot produces a conflict result
- Compatibility: additive optional fields only within this version
- Contract checks: planned schema validation and client/server contract checks; tool unavailable
- Result: blocked
"""
TASK = """# Reservation slice

## TASK-CORE-001 — Deliver reservation behavior

- Source: SPEC-CORE-001
- Goal: member can reserve an available slot
- Depends on: none
- Risk: concurrent requests can target the same slot
- Refine when: none — current task is detailed
- State: confirmed
- AC: AC-CORE-001
- Interfaces: IFACE-CORE-001
- Non-goals: recurring reservations
- Change scope: reservation module and member form; exclude billing
- Constraints: [architecture](../../ARCHITECTURE.md); preserve slot uniqueness
- Test plan: prepare behavior and conflict tests, implement, then run integration checks
- Done when: linked AC and contract checks have actual evidence; code review accepted
- Readiness: ready
- Completion: not-run
"""
LATER = """# Later cancellation

## TASK-CORE-002 — Add cancellation

- Source: SPEC-CORE-002
- Goal: cancel a reservation
- Depends on: TASK-CORE-001
- Risk: cancellation policy undecided
- Refine when: policy is approved after the first booking slice
"""
PASS = """
- Evidence: [execution report](../../reports/run.md)
- Tested revision: fixture-revision-123
- Executed on: 2026-09-12T10:00:00+08:00
"""


class SpecSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        build_valid_blueprint(self.root)
        (self.root / 'specs/core.md').unlink()
        self.domain = self.root / 'specs/core/reservation.md'
        self.interface = self.root / 'specs/interfaces/reservation.md'
        self.task = self.root / 'specs/tasks/reserve.md'
        self.write(self.domain, 'domain-spec', DOMAIN)
        self.write(self.interface, 'interface-spec', INTERFACE)
        self.write(self.task, 'task-spec', TASK)
        (self.root / 'contracts').mkdir()
        (self.root / 'contracts/reservation.json').write_text('{"type":"object","required":["slot_id"],"properties":{"slot_id":{"type":"string"}}}\n')
        (self.root / 'reports').mkdir()
        (self.root / 'reports/run.md').write_text('# Synthetic test fixture report\n')
        self.write(self.root / 'DESIGN.md', 'design', '## Applicability\n\nAPI-only slice, no user-facing UI.\n')
        self.replace(self.root / 'DESIGN.md', 'blueprint_kind: design', 'blueprint_kind: design\ndesign_stage: not-applicable')
        self.write_index()

    def write(self, path: Path, kind: str, body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(document(kind, body), encoding='utf-8')

    def replace(self, path: Path, before: str, after: str) -> None:
        original = path.read_text()
        self.assertIn(before, original)
        path.write_text(original.replace(before, after), encoding='utf-8')

    def write_index(self, current_specs='SPEC-CORE-001', current_tasks='TASK-CORE-001', ready='ready') -> None:
        index = document('spec-index', '''# Delivery

## Traceability

PRD-CORE-001
| SPEC-CORE-001, AC-CORE-001 | [behavior](specs/core/reservation.md) |
| IFACE-CORE-001 | [boundary](specs/interfaces/reservation.md) |
| TASK-CORE-001 | [task](specs/tasks/reserve.md) |

## Readiness ledger

| Gate | Status |
|---|---|
| design-ready | ready |
| implementation-ready | ''' + ready + ''' |
| production-ready | blocked |
''')
        index = index.replace('blueprint_kind: spec-index\n', f'blueprint_kind: spec-index\nspec_schema: 2\ndelivery_scope: first-reservation\ncurrent_specs: {current_specs}\ncurrent_tasks: {current_tasks}\n')
        (self.root / 'SPEC.md').write_text(index, encoding='utf-8')

    def findings(self):
        return MODULE.validate(self.root)

    def codes(self):
        return {item.code for item in self.findings() if item.severity != 'info'}

    def test_complete_current_slice_is_ready_before_tests_run(self):
        self.assertEqual(set(), self.codes())
        self.assertEqual('blocked', MODULE.record_field(INTERFACE, 'Result'))

    def test_nested_specs_and_typed_interfaces_tasks_are_discovered(self):
        (self.root / 'specs/core/README.md').write_text('# navigation\n')
        (self.root / 'specs/index.md').write_text('# helper\n')
        self.assertEqual(set(), self.codes())

    def test_future_work_can_remain_skeletal(self):
        self.write(self.root / 'specs/core/cancel.md', 'domain-spec', '## SPEC-CORE-002 — Cancel\n\n- Source: PRD-CORE-001\n- State: pending\n')
        self.write(self.root / 'specs/tasks/cancel.md', 'task-spec', LATER)
        with (self.root / 'SPEC.md').open('a') as f:
            f.write('\n| SPEC-CORE-002 | [cancel](specs/core/cancel.md) |\n| TASK-CORE-002 | [later](specs/tasks/cancel.md) |\n')
        self.assertEqual(set(), self.codes())

    def test_empty_scope_is_allowed_only_for_blocked_draft(self):
        self.write_index('none', 'none', 'blocked')
        self.assertEqual(set(), self.codes())
        self.replace(self.root / 'SPEC.md', '| implementation-ready | blocked |', '| implementation-ready | ready |')
        self.assertIn('SPEC_READINESS_CONFLICT', self.codes())

    def test_current_behavior_missing_ac_is_reported(self):
        self.replace(self.domain, DOMAIN, DOMAIN[:DOMAIN.index('### AC-')])
        self.assertTrue({'CURRENT_SPEC_WITHOUT_AC', 'SPEC_REFERENCE_UNKNOWN', 'TASK_READY_WITH_GAPS'} <= self.codes())

    def test_each_ac_requires_its_own_assertion_and_scenario(self):
        second = DOMAIN[DOMAIN.index('### AC-'):].replace('AC-CORE-001', 'AC-CORE-002')
        second = second[:second.index('- GIVEN')].replace('- Assertion: exactly one reservation belongs to that member\n', '')
        with self.domain.open('a') as f:
            f.write('\n' + second)
        with (self.root / 'SPEC.md').open('a') as f:
            f.write('\n| AC-CORE-002 | [behavior](specs/core/reservation.md) |\n')
        self.replace(self.task, '- AC: AC-CORE-001', '- AC: AC-CORE-001, AC-CORE-002')
        self.assertTrue({'AC_SCENARIO_MISSING', 'SPEC_FIELD_MISSING'} <= self.codes())

    def test_scenario_words_in_prose_are_not_executable_clauses(self):
        self.replace(self.domain, '- GIVEN an available slot\n- WHEN the member reserves it\n- THEN one reservation appears in their list',
                     'The review will check GIVEN/WHEN/THEN later.')
        self.assertIn('AC_SCENARIO_MISSING', self.codes())

    def test_untyped_domain_file_and_malformed_id_lists_are_not_silently_ignored(self):
        (self.root / 'specs/core/untyped.md').write_text('# Unclassified requirement\n')
        self.assertIn('INVALID_KIND', self.codes())
        self.replace(self.root / 'SPEC.md', 'current_tasks: TASK-CORE-001', 'current_tasks: [TASK-CORE-001]')
        self.assertIn('SPEC_REFERENCE_INVALID', self.codes())

    def test_manual_acceptance_requires_an_owner(self):
        self.replace(self.domain, '- Verification: automated', '- Verification: manual')
        self.assertIn('SPEC_FIELD_MISSING', self.codes())
        self.replace(self.domain, '- Verification: manual', '- Verification: manual\n- Acceptance owner: product owner')
        self.assertEqual(set(), self.codes())

    def test_ac_pass_requires_evidence_revision_and_date(self):
        self.replace(self.domain, '- Result: not-run', '- Result: passed')
        self.assertTrue({'SPEC_PASS_WITHOUT_EVIDENCE', 'SPEC_PASS_WITHOUT_REVISION', 'SPEC_PASS_WITHOUT_DATE'} <= self.codes())
        self.replace(self.domain, '- Result: passed', '- Result: passed\n' + PASS)
        self.assertEqual(set(), self.codes())
        self.replace(self.domain, '2026-09-12T10:00:00+08:00', '2026-02-30')
        self.assertIn('SPEC_PASS_WITHOUT_DATE', self.codes())

    def test_interface_pass_requires_a_real_record_not_a_command(self):
        self.replace(self.interface, '- Result: blocked', '- Result: passed')
        self.assertIn('SPEC_PASS_WITHOUT_EVIDENCE', self.codes())
        self.replace(self.interface, '- Result: passed', '- Result: passed\n' + PASS)
        self.assertEqual(set(), self.codes())

    def test_task_completion_pass_needs_evidence(self):
        self.replace(self.task, '- Completion: not-run', '- Completion: passed')
        self.assertIn('SPEC_PASS_WITHOUT_EVIDENCE', self.codes())
        self.replace(self.task, '- Completion: passed', '- Completion: passed\n' + PASS)
        self.assertEqual(set(), self.codes())

    def test_missing_contract_and_malformed_json_are_reported(self):
        contract = self.root / 'contracts/reservation.json'
        contract.write_text('{not json')
        self.assertIn('CONTRACT_JSON_INVALID', self.codes())
        contract.unlink()
        self.assertIn('BROKEN_LINK', self.codes())
        self.replace(self.interface, '[request schema](../../contracts/reservation.json)', 'pending')
        self.assertIn('INTERFACE_CONTRACT_MISSING', self.codes())

    def test_markdown_is_not_a_machine_contract(self):
        self.replace(self.interface, '../../contracts/reservation.json', '../../reports/run.md')
        self.assertIn('INTERFACE_CONTRACT_FORMAT', self.codes())

    def test_in_process_contract_can_explain_non_applicability(self):
        self.replace(self.interface, '- Protocol: JSON Schema', '- Protocol: in-process')
        self.replace(self.interface, '[request schema](../../contracts/reservation.json)', 'not-applicable: in-memory module boundary, no wire format')
        self.assertEqual(set(), self.codes())

    def test_yaml_and_proto_require_external_checks_not_automatic_execution(self):
        for suffix in ('yaml', 'proto'):
            with self.subTest(suffix=suffix):
                (self.root / f'contracts/reservation.{suffix}').write_text('test fixture; semantic validation intentionally not run\n')
                self.write(self.interface, 'interface-spec', INTERFACE.replace('reservation.json', f'reservation.{suffix}').replace('planned schema validation and client/server contract checks; tool unavailable', f'touch {self.root / "unexpected-execution"}'))
                self.assertEqual(set(), self.codes())
        self.assertFalse((self.root / 'unexpected-execution').exists())

    def test_duplicate_ids_and_orphan_ac_are_detected(self):
        self.write(self.root / 'specs/core/duplicate.md', 'domain-spec', DOMAIN)
        self.assertIn('DUPLICATE_SPEC_ID', self.codes())
        (self.root / 'specs/core/duplicate.md').unlink()
        self.replace(self.domain, '### AC-CORE-001', '## AC-CORE-001')
        self.assertIn('AC_PARENT_MISSING', self.codes())

    def test_unknown_references_and_task_ac_parent_mismatch_are_detected(self):
        self.replace(self.task, '- Depends on: none', '- Depends on: TASK-CORE-999')
        self.assertIn('SPEC_REFERENCE_UNKNOWN', self.codes())
        self.replace(self.task, '- Source: SPEC-CORE-001', '- Source: SPEC-CORE-999')
        self.assertIn('TASK_AC_SOURCE_MISMATCH', self.codes())

    def test_current_ac_coverage_cannot_be_satisfied_by_later_task(self):
        self.write_index(current_tasks='none', ready='blocked')
        self.assertIn('CURRENT_AC_UNCOVERED', self.codes())

    def test_missing_test_plan_prevents_task_ready(self):
        self.replace(self.task, '- Test plan: prepare behavior and conflict tests, implement, then run integration checks', '- Test plan:')
        self.assertTrue({'SPEC_FIELD_MISSING', 'TASK_READY_WITH_GAPS', 'SPEC_READINESS_CONFLICT'} <= self.codes())

    def test_self_dependency_and_longer_cycle_are_detected(self):
        self.replace(self.task, '- Depends on: none', '- Depends on: TASK-CORE-001')
        self.assertIn('TASK_DEPENDENCY_CYCLE', self.codes())
        self.replace(self.task, '- Depends on: TASK-CORE-001', '- Depends on: TASK-CORE-002')
        self.write(self.root / 'specs/tasks/second.md', 'task-spec', TASK.replace('TASK-CORE-001', 'TASK-CORE-002').replace('- Depends on: none', '- Depends on: TASK-CORE-001'))
        with (self.root / 'SPEC.md').open('a') as f:
            f.write('\n| TASK-CORE-002 | [second](specs/tasks/second.md) |\n')
        self.assertIn('TASK_DEPENDENCY_CYCLE', self.codes())

    def test_completed_external_dependency_can_be_reused(self):
        prerequisite = TASK.replace('TASK-CORE-001', 'TASK-CORE-002')
        self.write(self.root / 'specs/tasks/prerequisite.md', 'task-spec', prerequisite)
        with (self.root / 'SPEC.md').open('a') as f:
            f.write('\n| TASK-CORE-002 | [prerequisite](specs/tasks/prerequisite.md) |\n')
        self.replace(self.task, '- Depends on: none', '- Depends on: TASK-CORE-002')
        self.assertIn('TASK_DEPENDENCY_OUTSIDE_SCOPE', self.codes())
        self.replace(self.root / 'specs/tasks/prerequisite.md', '- Completion: not-run', '- Completion: passed\n' + PASS)
        self.assertEqual(set(), self.codes())

    def test_current_task_source_must_be_within_delivery_scope(self):
        self.write_index(current_specs='none', ready='blocked')
        self.assertIn('TASK_OUTSIDE_DELIVERY', self.codes())

    def test_one_task_per_file_and_definition_kinds_are_checked(self):
        with self.task.open('a') as f:
            f.write('\n## TASK-CORE-002 — second task\n\n- Source: SPEC-CORE-001\n')
        self.assertIn('TASK_FILE_CARDINALITY', self.codes())
        self.replace(self.task, 'blueprint_kind: task-spec', 'blueprint_kind: interface-spec')
        self.assertIn('SPEC_DEFINITION_KIND', self.codes())

    def test_retired_ac_stays_in_history_without_counting_as_current_coverage(self):
        replacement = DOMAIN[DOMAIN.index('### AC-'):].replace('AC-CORE-001', 'AC-CORE-002')
        self.replace(self.domain, '- Verification: automated', '- Superseded by: AC-CORE-002\n- Verification: automated')
        with self.domain.open('a') as f:
            f.write('\n' + replacement)
        with (self.root / 'SPEC.md').open('a') as f:
            f.write('\n| AC-CORE-002 | [new assertion](specs/core/reservation.md) |\n')
        self.assertIn('CURRENT_SPEC_SUPERSEDED', self.codes())
        self.replace(self.task, '- AC: AC-CORE-001', '- AC: AC-CORE-002')
        self.assertEqual(set(), self.codes())

    def test_root_metadata_is_not_a_definition_index(self):
        self.replace(self.root / 'SPEC.md', '| TASK-CORE-001 | [task](specs/tasks/reserve.md) |', '')
        self.assertIn('SPEC_INDEX_MISSING', self.codes())

    def test_unversioned_legacy_checks_and_invalid_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy = Path(directory)
            build_valid_blueprint(legacy)
            found = MODULE.validate(legacy)
            self.assertEqual([], [item for item in found if item.severity == 'error'])
            self.assertTrue(any(item.code == 'LEGACY_SPEC_SCHEMA' and item.severity == 'info' for item in found))
        for schema in ('', '1', '3', 'latest'):
            self.write_index()
            self.replace(self.root / 'SPEC.md', 'spec_schema: 2', 'spec_schema: ' + schema)
            self.assertIn('SPEC_SCHEMA_INVALID', self.codes())

    def test_cli_json_exit_code_and_read_only_behavior(self):
        before = {path: path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            result = MODULE.main([str(self.root), '--json'])
        self.assertEqual(0, result)
        self.assertEqual({'summary', 'findings'}, set(json.loads(stream.getvalue())))
        after = {path: path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(before, after)
        self.replace(self.task, '- Depends on: none', '- Depends on: TASK-CORE-001')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, MODULE.main([str(self.root)]))


if __name__ == '__main__':
    unittest.main()
