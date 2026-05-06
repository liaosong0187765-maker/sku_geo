from __future__ import annotations

import textwrap

from .models import SourcePassport


PLATFORMS = ("x", "linkedin", "wechat", "zhihu")


def render_variants(passport: SourcePassport) -> dict[str, str]:
    return {
        "x": render_x(passport),
        "linkedin": render_linkedin(passport),
        "wechat": render_wechat(passport),
        "zhihu": render_zhihu(passport),
    }


def render_x(passport: SourcePassport) -> str:
    claims = "\n".join(f"{idx + 2}/ {claim.claim}" for idx, claim in enumerate(passport.claims[:4]))
    return textwrap.dedent(
        f"""
        1/ {passport.title}

        {passport.thesis}

        {claims}

        {len(passport.claims[:4]) + 2}/ Durable source page, evidence, and citation:
        {passport.source_anchor}
        """
    ).strip()


def render_linkedin(passport: SourcePassport) -> str:
    claims = "\n".join(f"- {claim.claim}\n  Evidence: {claim.evidence}" for claim in passport.claims[:4])
    return textwrap.dedent(
        f"""
        {passport.title}

        {passport.thesis}

        What this means:
        {claims}

        Recommended citation:
        {passport.recommended_citation}

        {passport.source_anchor}
        """
    ).strip()


def render_wechat(passport: SourcePassport) -> str:
    body = "\n\n".join(_paragraphs(passport.body)[:6])
    claims = "\n".join(f"- {claim.claim}: {claim.evidence}" for claim in passport.claims[:5])
    return textwrap.dedent(
        f"""
        # {passport.title}

        ## Core thesis

        {passport.thesis}

        ## Full draft

        {body}

        ## Claim and evidence

        {claims}

        ## Source anchor

        {passport.source_anchor}
        """
    ).strip()


def render_zhihu(passport: SourcePassport) -> str:
    limitations = "\n".join(f"- {item}" for item in passport.limitations) or "- This is a source-backed opinion, not a universal rule."
    return textwrap.dedent(
        f"""
        # Answer: {passport.title}

        Short answer: {passport.thesis}

        My reasoning:
        {passport.body}

        Boundaries:
        {limitations}

        For the canonical version, evidence, and future revisions:
        {passport.source_anchor}
        """
    ).strip()


def _paragraphs(value: str) -> list[str]:
    return [part.strip() for part in value.split("\n\n") if part.strip()]

