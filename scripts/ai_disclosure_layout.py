"""Table-based disclosure layout adapted to the user's retained DOCX reference."""
STAGES = ["赛题理解与问题分析", "模型假设与符号定义", "模型建立与算法设计", "模型求解与编程实现",
          "结果分析与模型检验", "论文撰写与文字润色", "其他辅助环节（文献/数据/图表等）"]
MODES = ["网页对话框交互", "代码编辑器内嵌AI", "上传文件或数据对话", "AI智能体工作流（多步自动执行）", "其他方式"]
CATEGORIES = ["建模思路与方法建议", "公式推导与理论参考", "代码编写与调试", "结果分析与模型评价",
              "论文核心论述（摘要/结论等）", "其他内容"]
CORE = ["模型结构与创新点", "公式推导与求解步骤", "程序逻辑与参数设置", "结果分析与论文核心论述", "论文撰写与图表制作等"]


def validate_layout(data, filled):
    for rec in data["records"]:
        if rec.get("stage_group") not in STAGES:
            raise ValueError(f"记录 {rec['id']} 须选择有效 stage_group（7 个环节之一）")
        modes = rec.get("interaction_modes")
        if not isinstance(modes, list) or not modes or any(m not in MODES for m in modes):
            raise ValueError(f"记录 {rec['id']} 须填写 interaction_modes")
        if not filled(rec.get("response")):
            raise ValueError(f"记录 {rec['id']} 缺少 AI 回复核心内容 response")
        if rec.get("language_only") is not True and rec.get("output_category") not in CATEGORIES:
            raise ValueError(f"记录 {rec['id']} 须填写 output_category")
    selected = data.get("example_ids", [])
    ids = {r["id"] for r in data["records"]}
    if not isinstance(selected, list) or any(i not in ids for i in selected) or len(set(selected)) != len(selected):
        raise ValueError("example_ids 必须为不重复的实际记录 ID")
    leadership = data.get("core_leadership", [])
    if not isinstance(leadership, list) or len(leadership) != len(CORE):
        raise ValueError("须由团队逐项填写 5 个核心环节主导确认")
    for expected, row in zip(CORE, leadership):
        if row.get("stage") != expected or row.get("team_led") is not True or not filled(row.get("contribution")):
            raise ValueError(f"核心环节「{expected}」尚未由团队确认主导并说明贡献")


def render(data, preview, statement, escape):
    def table(headers, widths, rows):
        # Widths include cell padding: usable text width is 16 cm on A4.
        spec = "|" + "|".join(r">{\raggedright\arraybackslash}p{" + str(w) + "cm}" for w in widths) + "|"
        head = " & ".join(r"\textbf{" + escape(h) + "}" for h in headers) + r" \\ \hline"
        result = [r"{\small\begin{longtable}{" + spec + "}", r"\hline", head,
                  r"\endfirsthead", r"\hline", head, r"\endhead"]
        for row in rows:
            # Split large cell contents into continuation rows, allowing real prompts to span pages.
            chunks = []
            for value in row:
                value = str(value)
                chunks.append([value[i:i+240] for i in range(0, len(value), 240)] or [""])
            for i in range(max(map(len, chunks))):
                cells = [c[i] if i < len(c) else "" for c in chunks]
                if i and not cells[0]:
                    cells[0] = "续"
                result.append(" & ".join(escape(c) for c in cells) + r" \\ \hline")
        result.append(r"\end{longtable}}")
        return "\n".join(result)

    def heading(text):
        return r"\section*{" + escape(text) + "}"

    def hint(text):
        return r"{\small\itshape " + escape("【填写提示】" + text) + r"\par}\medskip" if preview else ""

    records = [] if preview else data["records"]
    body = [r"\begin{center}{\heiti\fontsize{22}{28}\selectfont 2026全国大学生数学建模竞赛\\[5pt]AI工具使用详情说明}\end{center}",
            r"\begin{center}\small 模板预览 · 不可提交\end{center}" if preview else escape(statement),
            heading("一、所用AI工具名称、版本或型号"),
            hint("列出全部实际使用的工具，版本或型号应可核实，主要用途用一句话概括。示范名称不计入使用记录。")]
    tools = {}
    for r in records:
        tools.setdefault((r["tool"], r["model"]), []).append(r["purpose"])
    rows = [[str(i), name, model, "；".join(dict.fromkeys(purposes))]
            for i, ((name, model), purposes) in enumerate(tools.items(), 1)]
    body.append(table(["序号", "AI工具名称", "版本/型号", "主要用途"], [.9, 3, 3, 7.1], rows or [[i, "", "", ""] for i in range(1, 5)]))
    body += [heading("二、具体使用目的和环节"), hint("逐一填写7个环节是否使用AI、具体目的和工具；未使用的环节如实注明。")]
    rows = []
    for i, stage in enumerate(STAGES, 1):
        matches = [r for r in records if r["stage_group"] == stage]
        rows.append([i, stage, "待填" if preview else ("是" if matches else "否"),
                     "" if preview else ("；".join(r["id"] + "：" + r["purpose"] for r in matches) or "未使用"),
                     "；".join(dict.fromkeys(r["tool"] for r in matches))])
    body.append(table(["序号", "论文写作环节", "是否使用", "使用目的", "使用工具"], [.9, 3.2, 1.3, 5.8, 2.5], rows))
    body += [r"\clearpage", heading("三、主要提示方式与使用过程说明"), r"\subsection*{（一）主要提示方式}",
             hint("按实际交互方式填写是或否，并说明使用场景，可多选。")]
    rows = []
    for i, mode in enumerate(MODES, 1):
        matches = [r for r in records if mode in r["interaction_modes"]]
        rows.append([i, mode, "待填" if preview else ("是" if matches else "否"),
                     "；".join(r["id"] + "：" + r["process"] for r in matches) or ("" if preview else "未使用")])
    body.append(table(["序号", "提示方式", "是否使用", "简要说明"], [.9, 4, 1.4, 7.7], rows))
    body += [r"\subsection*{（二）典型交互示例}", hint("建议选取2至3次关键交互，写明提示词、回复核心内容、处理方式与核验过程；不足2次时如实列出，不编造记录。")]
    ids = data.get("example_ids") or [r["id"] for r in records[:3]]
    examples = [r for identity in ids for r in records if r["id"] == identity] if not preview else [None, None]
    for i, r in enumerate(examples, 1):
        if preview and i > 1:
            body.append(r"\clearpage")
        body.append(r"\subsection*{示例" + str(i) + ("：" + escape(r["id"]) if r else "") + "}")
        labels = ["对应环节", "使用工具及版本", "交互时间", "本队提示词", "AI回复内容", "本队处理方式", "人工核验方式"]
        values = ([r["stage"], r["tool"] + " / " + r["model"], r["date"], r["prompt"], r["response"],
                   r.get("adoption", "") + "；" + r.get("modification", ""),
                   ("纯语言润色，免列本项详情。" if r.get("language_only") is True else r["verification"] + "；证据：" + r["evidence"])]
                  if r else ["填写具体环节", "填写实际工具及型号", "填写实际交互时间", "完整记录主要提示词，不含账号密码或密钥。",
                             "记录回复核心内容；输出位置可另附相对路径。", "直接采纳 / 修改后采纳 / 未采纳，并说明修改内容或弃用原因。",
                             "说明独立推导、复现、交叉核对等实际核验过程及证据。"])
        body.append(table(["项目", "填写内容"], [3.1, 11.5], list(zip(labels, values))))
    body += [r"\clearpage", heading("四、对AI输出的采纳、人工修改和核验的主要情况"),
             hint("对非纯语言润色输出逐项说明采纳范围、人工修改和核验依据，不能只写“已核验”。")]
    rows = []
    for i, category in enumerate(CATEGORIES, 1):
        matches = [r for r in records if not r.get("language_only") and r["output_category"] == category]
        rows.append([i, category, "\n".join(r["id"] + "：" + r["adoption"] + "；" + r["modification"] for r in matches) or ("" if preview else "无此类输出"),
                     "\n".join(r["id"] + "：" + r["verification"] + "；" + r["evidence"] + "；核验角色：" + r["reviewer_role"] for r in matches)])
    body.append(table(["序号", "AI输出内容类别", "采纳与修改情况", "人工核验方式"], [.9, 3.2, 4.9, 5], rows))
    body += [r"\subsection*{核心环节人工主导确认}", hint("由团队逐项确认并说明具体贡献，AI不得代填确认。")]
    rows = [[i, stage, "待确认" if preview else "是", "" if preview else data["core_leadership"][i-1]["contribution"]] for i, stage in enumerate(CORE, 1)]
    body.append(table(["序号", "核心环节", "是否本队主导", "本队贡献说明"], [.9, 4, 2.1, 7], rows))
    confirmation = "本队确认：以上AI工具使用情况真实完整，无隐瞒、无虚假陈述。核心建模与分析由本队主导完成，所有AI输出内容（语言润色除外）均经过人工审查与核实。如有不实，本队愿承担相应责任。"
    body.append(escape("确认文字预览（尚未确认）：" + confirmation if preview else confirmation))
    # Preserve process/output provenance for all records even when not chosen as typical examples.
    if records:
        body += [r"\clearpage", heading("使用过程与输出定位补充")]
        for r in records:
            body += [r"\subsection*{" + escape(r["id"]) + "}",
                     escape("使用过程：" + r["process"]) + r"\par\medskip",
                     escape("输出位置及摘要：" + r["output"]) + r"\par\medskip"]
    return "\n".join([r"\documentclass[UTF8,a4paper,11pt,fontset=fandol]{ctexart}",
                       r"\usepackage[margin=2.5cm]{geometry}", r"\usepackage{array,longtable}",
                       r"\ctexset{section={format=\heiti\zihao{4},beforeskip=12pt,afterskip=7pt},subsection={format=\heiti\zihao{-4},beforeskip=9pt,afterskip=5pt}}",
                       r"\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.45}",
                       r"\setlength{\LTpre}{5pt}\setlength{\LTpost}{7pt}",
                       r"\setlength{\emergencystretch}{3em}\pagestyle{plain}",
                       r"\begin{document}", *body, r"\end{document}"])
