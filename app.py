import os
import uuid
from typing import Annotated, Optional
from pathlib import Path
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from main import solve_issue

app = FastAPI(title="Agentic AI Go Fixer", version="1.0.0")
jobs = {}

class IssueRequest(BaseModel):
    issue: Annotated[str, Field(..., description="GitHub issue text to fix")]
    repo: Annotated[Optional[str], Field(default=None, description="Path to the target Go repo")]
    output: Annotated[Optional[str], Field(default=None, description="Directory for output artefacts")]


def run_job(job_id: str, issue: str, repo: Optional[str], output: Optional[str]):
    try:
        jobs[job_id]["status"] = "running"
        result = solve_issue(
            issue=issue,
            repo=repo,
            output=output
        )
        jobs[job_id] = {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        jobs[job_id] = {
            "status": "failed",
            "error": str(e)
        }


@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agentic AI Go Fixer</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    pre, code { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">
  <header class="border-b border-slate-800 bg-slate-950/70 backdrop-blur sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 font-bold text-xl text-white">
          Go
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            Agentic AI Go Fixer
            <span class="text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-medium">Online</span>
          </h1>
          <p class="text-xs text-slate-400">Autonomous Issue Retrieval, LLM Fix Planning, Code Patching & Go Validation</p>
        </div>
      </div>
      <div class="flex items-center space-x-3 text-sm">
        <a href="/docs" target="_blank" class="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 transition text-slate-200">
          Swagger /docs
        </a>
        <a href="https://github.com/shreykumarsingh/Agentic-fo-fixer-" target="_blank" class="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition">
          GitHub Repo
        </a>
      </div>
    </div>
  </header>

  <main class="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
    <!-- Left Column: Input Form -->
    <section class="lg:col-span-5 space-y-6">
      <div class="bg-slate-800/60 border border-slate-700/70 rounded-2xl p-6 shadow-xl backdrop-blur">
        <h2 class="text-base font-semibold text-white mb-2 flex items-center gap-2">
          <span>🛠️</span> Submit a Go Issue
        </h2>
        <p class="text-xs text-slate-400 mb-4">
          Describe a bug or feature. The agent will retrieve relevant Go files from the index, plan a fix, apply a patch, run <code class="text-cyan-400">go vet & go test</code>, and generate a pull request.
        </p>

        <form id="issueForm" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold uppercase text-slate-300 mb-1.5">Issue Description</label>
            <textarea id="issueInput" rows="5" required
              class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
              placeholder="e.g. Fix excluded_if validation tag failing when checking optional nil pointer fields..."></textarea>
          </div>

          <!-- Quick Samples -->
          <div>
            <span class="text-xs font-medium text-slate-400 block mb-1.5">Try an example:</span>
            <div class="flex flex-wrap gap-2">
              <button type="button" onclick="setExample(1)" class="text-xs px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700 text-cyan-300 hover:border-cyan-500 transition">
                ⚡ Excluded_if Nil Pointer
              </button>
              <button type="button" onclick="setExample(2)" class="text-xs px-2.5 py-1 rounded-md bg-slate-900 border border-slate-700 text-cyan-300 hover:border-cyan-500 transition">
                ⚡ Baked-in Currency Check
              </button>
            </div>
          </div>

          <button id="submitBtn" type="submit"
            class="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-500/25 transition flex items-center justify-center gap-2">
            <span>🚀 Run Agent Pipeline</span>
          </button>
        </form>
      </div>

      <!-- Pipeline Info -->
      <div class="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-5 text-xs text-slate-400 space-y-3">
        <h3 class="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">Workflow Steps</h3>
        <ol class="space-y-2 list-decimal list-inside text-slate-300">
          <li><strong class="text-cyan-400">Analyzer / Retriever:</strong> 3-dimension scoring on AST symbols & filenames.</li>
          <li><strong class="text-cyan-400">Planner (Gemini):</strong> Ranks files and drafts a step-by-step fix plan.</li>
          <li><strong class="text-cyan-400">Coder (Gemini):</strong> Generates unified patch & applies it.</li>
          <li><strong class="text-cyan-400">Test Runner:</strong> Executes <code class="text-emerald-400">go vet ./...</code> and <code class="text-emerald-400">go test ./...</code>.</li>
          <li><strong class="text-cyan-400">PR Generator:</strong> Compiles conventional commit title & PR summary.</li>
        </ol>
      </div>
    </section>

    <!-- Right Column: Live Output & Results -->
    <section class="lg:col-span-7 space-y-6">
      <div id="statusCard" class="bg-slate-800/60 border border-slate-700/70 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between pb-4 border-b border-slate-700/60 mb-4">
          <div class="flex items-center space-x-2">
            <span class="text-lg">📊</span>
            <h2 class="font-semibold text-white">Execution Output</h2>
          </div>
          <span id="badgeStatus" class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700 font-medium">Idle</span>
        </div>

        <div id="idleState" class="py-16 text-center text-slate-500">
          <div class="text-4xl mb-3">🤖</div>
          <p class="text-sm font-medium">Submit an issue on the left to start the autonomous agent pipeline.</p>
        </div>

        <div id="runningState" class="hidden py-12 text-center">
          <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-cyan-500 border-t-transparent mb-4"></div>
          <p class="text-sm font-semibold text-cyan-400">Agent is analyzing repository and planning fix...</p>
          <p class="text-xs text-slate-400 mt-1">This typically takes 20–40 seconds depending on LLM responses and Go test suites.</p>
        </div>

        <div id="resultsState" class="hidden space-y-4">
          <!-- Summary Box -->
          <div class="p-4 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-between">
            <div>
              <span class="text-xs text-slate-400 block">Target File Selected</span>
              <span id="resFile" class="text-sm font-mono text-cyan-300 font-bold"></span>
            </div>
            <div>
              <span class="text-xs text-slate-400 block">Go Validation</span>
              <span id="resTests" class="text-xs font-semibold px-2 py-0.5 rounded-full"></span>
            </div>
          </div>

          <!-- Tabs -->
          <div class="flex border-b border-slate-700 text-xs font-medium space-x-1" id="tabBar">
            <button onclick="switchTab('plan')" id="tabBtn-plan" class="px-3 py-2 border-b-2 border-cyan-500 text-cyan-400">Fix Plan</button>
            <button onclick="switchTab('patch')" id="tabBtn-patch" class="px-3 py-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200">Diff Patch</button>
            <button onclick="switchTab('tests')" id="tabBtn-tests" class="px-3 py-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200">Test Results</button>
            <button onclick="switchTab('pr')" id="tabBtn-pr" class="px-3 py-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200">PR Summary</button>
          </div>

          <div id="tabContent-plan" class="tab-pane bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-300 overflow-x-auto max-h-96 whitespace-pre-wrap font-mono"></div>
          <div id="tabContent-patch" class="tab-pane hidden bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-emerald-300 overflow-x-auto max-h-96 whitespace-pre-wrap font-mono"></div>
          <div id="tabContent-tests" class="tab-pane hidden bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-300 overflow-x-auto max-h-96 whitespace-pre-wrap font-mono"></div>
          <div id="tabContent-pr" class="tab-pane hidden bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs text-slate-300 overflow-x-auto max-h-96 whitespace-pre-wrap font-mono"></div>
        </div>

        <div id="errorState" class="hidden p-4 rounded-xl bg-red-950/40 border border-red-800 text-xs text-red-200">
          <p class="font-bold text-red-400 mb-1">Execution Error:</p>
          <pre id="errorText" class="whitespace-pre-wrap"></pre>
        </div>
      </div>
    </section>
  </main>

  <script>
    const examples = {
      1: "Fix excluded_if validation tag failing when checking optional nil pointer fields in validator/baked_in.go",
      2: "Add validation check for ISO-4217 currency codes to prevent panic on empty string"
    };

    function setExample(id) {
      document.getElementById('issueInput').value = examples[id];
    }

    function switchTab(name) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('#tabBar button').forEach(el => {
        el.className = "px-3 py-2 border-b-2 border-transparent text-slate-400 hover:text-slate-200";
      });
      document.getElementById('tabContent-' + name).classList.remove('hidden');
      document.getElementById('tabBtn-' + name).className = "px-3 py-2 border-b-2 border-cyan-500 text-cyan-400";
    }

    let pollInterval = null;

    document.getElementById('issueForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const issue = document.getElementById('issueInput').value.trim();
      if (!issue) return;

      const submitBtn = document.getElementById('submitBtn');
      submitBtn.disabled = true;
      submitBtn.classList.add('opacity-50');

      document.getElementById('idleState').classList.add('hidden');
      document.getElementById('resultsState').classList.add('hidden');
      document.getElementById('errorState').classList.add('hidden');
      document.getElementById('runningState').classList.remove('hidden');

      const badge = document.getElementById('badgeStatus');
      badge.textContent = "Queued";
      badge.className = "text-xs px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 font-medium";

      try {
        const resp = await fetch('/solve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ issue: issue })
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || 'Failed to submit issue');

        pollJob(data.job_id);
      } catch (err) {
        showError(err.message);
      }
    });

    function pollJob(jobId) {
      clearInterval(pollInterval);
      pollInterval = setInterval(async () => {
        try {
          const resp = await fetch('/jobs/' + jobId);
          const data = await resp.json();

          const badge = document.getElementById('badgeStatus');
          badge.textContent = data.status.toUpperCase();

          if (data.status === 'running') {
            badge.className = "text-xs px-2.5 py-1 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 font-medium animate-pulse";
          } else if (data.status === 'completed') {
            clearInterval(pollInterval);
            badge.className = "text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium";
            showResults(data.result);
          } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            badge.className = "text-xs px-2.5 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 font-medium";
            showError(data.error);
          }
        } catch (err) {
          clearInterval(pollInterval);
          showError(err.message);
        }
      }, 3000);
    }

    function showResults(res) {
      document.getElementById('runningState').classList.add('hidden');
      document.getElementById('resultsState').classList.remove('hidden');
      document.getElementById('submitBtn').disabled = false;
      document.getElementById('submitBtn').classList.remove('opacity-50');

      document.getElementById('resFile').textContent = res.selected_file || 'None';
      const testsSpan = document.getElementById('resTests');
      if (res.tests_passed) {
        testsSpan.textContent = "ALL PASSED ✓";
        testsSpan.className = "text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
      } else {
        testsSpan.textContent = "CHECKS FAILED ✗";
        testsSpan.className = "text-xs font-semibold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30";
      }

      document.getElementById('tabContent-plan').textContent = res.plan || 'No plan generated.';
      document.getElementById('tabContent-patch').textContent = res.patch || 'No patch diff available.';
      document.getElementById('tabContent-tests').textContent = res.test_results || 'No test results.';
      document.getElementById('tabContent-pr').textContent = res.pr_summary || 'No PR summary.';
      switchTab('plan');
    }

    function showError(err) {
      document.getElementById('runningState').classList.add('hidden');
      document.getElementById('errorState').classList.remove('hidden');
      document.getElementById('errorText').textContent = err;
      document.getElementById('submitBtn').disabled = false;
      document.getElementById('submitBtn').classList.remove('opacity-50');
    }
  </script>
</body>
</html>
"""

@app.post("/solve")
def solve_request(
    request: IssueRequest,
    background_tasks: BackgroundTasks
):
    try:
        job_id = str(uuid.uuid4())
        jobs[job_id] = {"status": "queued"}

        background_tasks.add_task(
            run_job,
            job_id,
            request.issue,
            request.repo,
            request.output
        )

        return {
            "job_id": job_id,
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    return jobs[job_id]
