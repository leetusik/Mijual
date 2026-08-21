"""``mijual.present`` — the presentation contract, between the pipeline and every surface.

P2 persisted *what the filings say*. The signed P3 design names shapes that P2
does not store — ``countdown.label_ko``, ``offering_inputs``, ``lapse_result``,
``corp_name_agrees_with_body`` — and every one of them is a **derivation** over
what P2 already wrote. This package is that derivation, and it is one package
rather than a convention each endpoint re-implements, because R4 names the
failure mode out loud: *two divergent readouts for the same number*.

### What it is

**Pure.** No HTTP, no SQL, no clock unless one is passed. Every function takes
inputs a caller has already loaded — an
:class:`~mijual.gates.exposure.EventExposure`, a
:class:`~mijual.cb.ConvertibleFacts`, an ``EventInputs`` / ``LapseRow`` from
:mod:`mijual.estimate`, a stored ``PerformanceReport.facts`` mapping, a reference
date — and returns frozen dataclasses that serialize themselves. A derivation
that seems to want a ``Session`` is a derivation that has not been handed its
rows yet.

**Import-light, on purpose.** At runtime this package imports :mod:`mijual.calc`
and :mod:`mijual.gates.exposure` and nothing else of the pipeline.
:mod:`mijual.estimate` pulls :mod:`mijual.dart`, :mod:`mijual.collect` and
:mod:`mijual.extract` at module level (measured), and this layer sits on a
request path, where the `architecture` boundary forbids a module that can spend
an OpenDART request or a model call. So those types are ``TYPE_CHECKING``-only
and the functions read attributes.

**One direction.** ``web`` depends on ``present``; ``present`` never depends on
``web``. Serialization-to-string of *instants* is therefore restated in
:func:`mijual.present.values.instant` rather than imported from
:mod:`mijual.web.clock` — same policy, pinned together by the test suite.

### What it makes structural

Four of the product's trust rules stop being things a frontend author must
remember and become things the contract cannot express otherwise:

* **an estimate never renders untagged, a fact never carries the mark** —
  :class:`~mijual.present.values.Figure` has no default for ``estimated``, and
  refuses to attach a verbatim quote to a derived number;
* **money never appears before 확정발행가** —
  :class:`~mijual.present.money.OfferingInputs` and
  :class:`~mijual.present.money.LapseResult` will not construct with a won figure
  and no confirmed price, mail and every other surface included;
* **a gate-blocked field is absent, not blank** —
  :func:`~mijual.present.event.field_payloads` reads ``renderable_fields``, so
  there is no key to render a placeholder into; and **추후결정 carries no date**,
  which :class:`~mijual.present.event.FieldPayload` refuses at construction;
* **D-days are computed upstream, in KST, per rights type** —
  :func:`~mijual.present.event.countdown_of` picks the governing anchor (① 증서
  매매 마감 · ② 전환청구 **개시** · ③ 반대의사 통지 마감), reports the reference
  day it used, and emits machine ``window_state`` tokens instead of Korean, so a
  past ② opening can only mean 진행 중.

### Where the Korean comes from

Nothing here invents a Korean string. :data:`~mijual.present.event.FIELD_NAMES_KO`
is copied verbatim from :data:`mijual.extract.fields.FIELDS` (and pinned to it by
``tests/test_present.py``), :data:`~mijual.present.event.COUNTDOWN_LABELS_KO` and
:data:`~mijual.present.money.MISMATCH_LABEL_KO` are the strings the P3 grounding
pack was exported with, and the 철회 notices come from
:data:`mijual.gates.exposure.WITHDRAWN_NOTICE_KO`. Every other user-visible
sentence belongs to the signed design and is the surface's to render.

### Serializing

Use each shape's ``payload()``. It is where "an absent value is **absent**, never
``null``" is enforced; ``dataclasses.asdict`` would emit the nulls the contract
exists to prevent.
"""

from __future__ import annotations

from mijual.present.event import (
    COUNTDOWN_LABELS_KO,
    COUNTDOWN_SOURCES,
    FIELD_NAMES_KO,
    RENDERABLE_STATES,
    Countdown,
    EventView,
    FieldPayload,
    Identity,
    countdown_of,
    event_view,
    field_payloads,
    field_value,
    identity_of,
)
from mijual.present.money import (
    MISMATCH_LABEL_KO,
    Disagreement,
    LapseResult,
    OfferingInputs,
    Reading,
    issuer_disagreement,
    lapse_result,
    offering_inputs,
)
from mijual.present.summary import URGENT_DAYS, BoardSummary, board_summary
from mijual.present.values import Figure, decimal_str, instant, iso_day, to_decimal

__all__ = [
    "COUNTDOWN_LABELS_KO",
    "COUNTDOWN_SOURCES",
    "FIELD_NAMES_KO",
    "MISMATCH_LABEL_KO",
    "RENDERABLE_STATES",
    "URGENT_DAYS",
    "BoardSummary",
    "Countdown",
    "Disagreement",
    "EventView",
    "FieldPayload",
    "Figure",
    "Identity",
    "LapseResult",
    "OfferingInputs",
    "Reading",
    "board_summary",
    "countdown_of",
    "decimal_str",
    "event_view",
    "field_payloads",
    "field_value",
    "identity_of",
    "instant",
    "iso_day",
    "issuer_disagreement",
    "lapse_result",
    "offering_inputs",
    "to_decimal",
]
