#!/usr/bin/env python3
"""V5. The handover guide: what is done, and what only Dr. Rizvi can do."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, ListFlowable, ListItem,
                                PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

OUT = Path("/mnt/user-data/outputs/TTS_Submission_Guide.pdf")
INK = colors.HexColor("#1F2A37")
ACC = colors.HexColor("#0072B2")
WARN = colors.HexColor("#C2410C")

ss = getSampleStyleSheet()
S = {
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="Times-Bold",
                         fontSize=15, leading=18, textColor=INK,
                         spaceBefore=14, spaceAfter=6),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="Times-Bold",
                         fontSize=11.5, leading=14, textColor=ACC,
                         spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", parent=ss["BodyText"], fontName="Times-Roman",
                        fontSize=10, leading=13.6, alignment=TA_JUSTIFY,
                        textColor=INK, spaceAfter=6),
    "li": ParagraphStyle("li", parent=ss["BodyText"], fontName="Times-Roman",
                         fontSize=10, leading=13.4, alignment=TA_JUSTIFY,
                         textColor=INK, spaceAfter=3),
    "warn": ParagraphStyle("warn", parent=ss["BodyText"],
                           fontName="Times-Roman", fontSize=10, leading=13.6,
                           alignment=TA_JUSTIFY, textColor=WARN, spaceAfter=6),
    "title": ParagraphStyle("title", parent=ss["Title"], fontName="Times-Bold",
                            fontSize=20, leading=24, textColor=INK,
                            spaceAfter=2),
    "sub": ParagraphStyle("sub", parent=ss["Normal"], fontName="Times-Italic",
                          fontSize=11, leading=14, textColor=ACC,
                          spaceAfter=12),
    "cap": ParagraphStyle("cap", parent=ss["Normal"], fontName="Times-Roman",
                          fontSize=8.5, leading=11, textColor=INK),
    "capb": ParagraphStyle("capb", parent=ss["Normal"], fontName="Times-Bold",
                           fontSize=8.5, leading=11, textColor=INK),
}


def P(t, s="p"):
    return Paragraph(t, S[s])


def bullets(items, style="li"):
    return ListFlowable([ListItem(P(i, style), leftIndent=12) for i in items],
                        bulletType="bullet", start="square",
                        leftIndent=14, bulletFontSize=6,
                        bulletColor=ACC, spaceAfter=6)


def tbl(rows, widths, head=True):
    data = [[Paragraph(c, S["capb" if (head and r == 0) else "cap"])
             for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, INK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F4F6F8")]),
    ]))
    return t


F = []
F += [P("Submitting to IEEE Transactions on Technology and Society", "title"),
      P("What is finished, what is left, and the four things only you can "
        "do &mdash; 7 October 2026", "sub"),
      HRFlowable(width="100%", color=ACC, thickness=1.1, spaceAfter=10)]

F += [P("The short version", "h1"),
      P("The manuscript has been rebuilt around the decomposition result and "
        "now carries both datasets. It is <b>9 pages</b> against TTS's "
        "10-page limit, which is inclusive of references, biographies, "
        "figures and tables, so there is about a page of headroom and no "
        "overlength charge. Four items remain, all of them things that "
        "require your institution or your signature rather than more "
        "analysis. Three of those four block submission."),
      P("The file to submit is <b>Manuscript_TTS.docx</b>. TTS does not "
        "accept LaTeX &mdash; its author information page states that "
        "submissions must be in .DOC format using the IEEE transactions "
        "template &mdash; so the deliverable this time is a Word file, not a "
        "PDF. The PDF in the package is the same document rendered for "
        "reading and for your co-authors; do not submit it in place of the "
        "Word file.")]

F += [P("Why the paper changed shape", "h1"),
      P("The T-BIOM version led with a model: a geometry-guided architecture, "
        "with the fairness audit as one of several results. That framing was "
        "the weaker of the two available, because the strongest thing the "
        "work now contains is not the model. It is the finding that a "
        "subgroup accuracy gap is not a property of a model at all, and that "
        "two datasets producing similar-looking gaps warrant opposite "
        "conclusions."),
      P("TTS publishes work on the societal consequences of technology, and "
        "the audience it reaches &mdash; people who read audits and act on "
        "them &mdash; is the audience this result is for. The paper now "
        "argues a methodological and governance point and uses facial "
        "aesthetic assessment as the setting in which to demonstrate it. The "
        "architecture material is still present, compressed into one results "
        "subsection, because it earns its place: interpretable geometry "
        "degrades 11% on an unseen population where the appearance embedding "
        "degrades 51%, and that is an auditing-relevant property."),
      P("<b>Concretely, what is new since the T-BIOM draft:</b>"),
      bullets([
          "SCUT-FBP5500 is now a second full dataset, not a validation "
          "aside: 5,429 faces at 98.7% retention, four subgroups, all 330,000 "
          "individual ratings used for the label-side analysis.",
          "The sampling-noise floor is a first-class quantity with its own "
          "estimator, its own table, and a significance test. It accounts for "
          "51% of the MEBeauty gap and 28% of the SCUT one.",
          "Every correction is validated against a known answer at "
          "n = 200,000 before it is applied to real data (Table I). This was "
          "the single largest hole in the previous draft.",
          "The surviving SCUT disparity is attributed: balancing the training "
          "mix removes 67% of it for 0.012 of pooled accuracy.",
          "A new Section VI sets out what a subgroup audit should report, "
          "including the point that correction is diagnosis and not remedy "
          "&mdash; the people served worse are still served worse. Reviewers "
          "at this venue will look for exactly that distinction, and a paper "
          "that corrects a disparity without making it reads as explaining "
          "the disparity away.",
      ])]

F += [PageBreak()]
F += [P("The four things only you can do", "h1"),
      P("Three of these block submission. I have marked each one with what "
        "the editor checks for.", "warn")]

F += [P("1. Ethics determination &mdash; blocking", "h2"),
      P("Section VII ends with a bracketed placeholder: "
        "<i>[REFERENCE NUMBER]</i>, issued <i>[DATE]</i>, by the "
        "institutional review body of Brainware University. Both datasets are "
        "public and no new human-subject data was collected, so an exemption "
        "or a determination of non-applicability is the likely outcome, but "
        "IEEE's editorial check looks for a reference number on any "
        "human-subject-derived data and a submission without one is "
        "routinely held. Request it now; the turnaround is usually the long "
        "pole. If your review body issues an exemption rather than an "
        "approval, say so in those words &mdash; an honest exemption reads "
        "better than a vague approval.")]

F += [P("2. The repository and its DOI &mdash; blocking", "h2"),
      P("The same sentence carries <i>[REPOSITORY URL]</i> and <i>[DOI]</i>. "
        "The <font face='Courier'>fbpgeo</font> package and every analysis "
        "script in this package need to be published and then archived to "
        "mint a DOI. The usual route is a public GitHub repository, then a "
        "Zenodo release linked to it, which issues the DOI automatically. I "
        "could not do this from here: Zenodo, figshare and the other archives "
        "are outside the network this session can reach, and in any case the "
        "repository has to be owned by you. <b>Do not invent a URL to fill "
        "the placeholder</b> &mdash; reviewers check them, and a dead link in "
        "a paper about auditing standards is the worst possible place for "
        "one.")]

F += [P("3. The author contributions statement &mdash; blocking", "h2"),
      P("There is no contributions statement in the current draft, and I have "
        "deliberately not written one. I do not know what T. Fatima and "
        "S. Talat each did, and the paper has changed so much since the "
        "T-BIOM version that any statement carried over would be wrong. "
        "Write two or three sentences in CRediT terms (conceptualization, "
        "methodology, software, formal analysis, writing) and add them above "
        "the References. Note that the analytical contribution is now "
        "concentrated in the measurement-error and simulation work, so the "
        "statement should reflect who did that.")]

F += [P("4. SCUT-FBP5500 terms of use", "h2"),
      P("The dataset's licence requires citation of Liang et al., ICPR 2018, "
        "which the paper does (reference 29, and again in Section VII under "
        "Data and ethics). Confirm there is no separate data-use agreement "
        "you signed that imposes further conditions &mdash; some releases "
        "restrict redistribution of derived landmark files, which matters for "
        "what you put in the public repository. If in doubt, publish the "
        "code and the extraction scripts but not the extracted geometry "
        "tables, and say so in the repository README.")]

F += [P("Two smaller things worth checking", "h1")]
F += [bullets([
    "<b>One reference I could not fully verify.</b> Reference 13, Jacobs and "
    "Wallach, &ldquo;Measurement and fairness,&rdquo; FAccT 2021: the venue, "
    "year and DOI (10.1145/3442188.3445901) are confirmed, but the page range "
    "375&ndash;385 I could not read off the publisher's record, because the "
    "ACM Digital Library page was rate-limited when I tried. The range is "
    "consistent with the paper's stated length of 11 pages. Check it in the "
    "ACM DL before submitting. Every other reference carries details I "
    "verified or that were verified in the earlier rounds.",
    "<b>The official IEEE template.</b> The .docx reproduces IEEE's "
    "Transactions page metrics directly &mdash; US Letter, 0.75 in top "
    "margin, two 3.5 in columns with a 0.2 in gutter, 10 pt Times &mdash; "
    "because the template file itself was not reachable from this "
    "environment. It will look right to a reviewer as it stands. If you want "
    "the genuine article, download the Word template from the IEEE Author "
    "Center, open both, and paste the body across; no text, table or figure "
    "needs to change, and the page count will land within half a page of 9.",
])]

F += [PageBreak()]
F += [P("What is in the package", "h1")]
F += [tbl([
    ["File", "What it is"],
    ["<b>Manuscript_TTS.docx</b>",
     "<b>The submission file.</b> 9 pages, IEEE Transactions layout, "
     "47 references, 4 tables, 5 figures."],
    ["Manuscript_TTS.pdf",
     "The same document rendered for reading. Not for submission."],
    ["figs/*.png, *.pdf",
     "The five figures at 600 dpi, drawn at final column width so nothing is "
     "rescaled by the typesetter."],
    ["src/v1_validate.py",
     "The known-answer validation behind Table I and the noise floor behind "
     "Table II. Re-runs in about two minutes."],
    ["src/v2_figs.py", "Regenerates every figure from the result files."],
    ["src/v3_docx.py, v4_build.py",
     "The layout engine and the assembler. Every table in the paper is "
     "generated from a results CSV, so no number is typed by hand."],
    ["src/manuscript.txt",
     "The text itself, in a light markup. <b>Edit here</b>, then re-run "
     "v4_build.py, rather than editing the .docx &mdash; otherwise your "
     "changes are lost the next time it is rebuilt."],
    ["results/", "The validation outputs the tables are built from."],
], [38, 110])]

F += [Spacer(1, 8)]
F += [P("How to make a change", "h1"),
      P("If you want to edit the wording, change "
        "<font face='Courier'>src/manuscript.txt</font> and run:"),
      P("<font face='Courier'>python3 src/v4_build.py</font>"),
      P("which re-numbers the references by order of first appearance, "
        "rebuilds the tables from the result files, re-renders the .docx and "
        "converts it to PDF. Citations in the text are written as "
        "<font face='Courier'>[liang2018]</font> and resolved automatically; "
        "if you cite a key that has no entry, the build stops and tells you "
        "rather than producing a silent gap.")]

F += [P("If TTS declines", "h1"),
      P("The obvious second venue is ACM FAccT, and the paper is already "
        "close to its shape: a measurement-and-method argument with a "
        "governance section. FAccT wants its own format and tends to want the "
        "practice implications foregrounded, so Section VI would move up and "
        "the architecture subsection (V-E) would be cut to a paragraph. The "
        "deadline cycle is the constraint there, not the fit."),
      P("A third option, if you would rather stay with a technical venue, is "
        "to split: the decomposition and the two-dataset result to TTS or "
        "FAccT, and the geometry-versus-appearance transfer result to T-BIOM "
        "as a shorter paper of its own. I would not do this unless TTS "
        "declines, because the transfer result is currently earning its keep "
        "by showing that the auditing argument has a design consequence.")]

F += [Spacer(1, 10), HRFlowable(width="100%", color=ACC, thickness=0.8),
      Spacer(1, 4),
      P("<i>Prepared alongside the manuscript. Every figure in the "
        "manuscript was checked visually at final size, and every number in "
        "the text and tables is written from a result file rather than "
        "transcribed.</i>", "cap")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, topMargin=18 * mm,
                        bottomMargin=18 * mm, leftMargin=20 * mm,
                        rightMargin=20 * mm,
                        title="TTS Submission Guide",
                        author="Prepared for Q. M. Rizvi")
doc.build(F)
print("wrote", OUT)
