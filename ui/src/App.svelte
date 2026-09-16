<script>
  import { onMount } from "svelte";
  import { projectBridge } from "./lib/projectBridge.js";

  let manuscript = "";
  let units = [];
  let loading = true;
  let error = "";
  let syncTimer;

  function applyView(view) {
    manuscript = view.manuscript;
    units = view.units;
  }

  onMount(async () => {
    try {
      applyView(await projectBridge.loadProjectState());
    } catch (reason) {
      error = String(reason);
    } finally {
      loading = false;
    }
  });

  function manuscriptChanged() {
    clearTimeout(syncTimer);
    syncTimer = setTimeout(async () => {
      try {
        error = "";
        applyView(await projectBridge.syncManuscript(manuscript));
      } catch (reason) {
        error = String(reason);
      }
    }, 250);
  }

  async function setUnitVoice(unitId, voiceId) {
    try {
      error = "";
      applyView(await projectBridge.setUnitVoice(unitId, voiceId));
    } catch (reason) {
      error = String(reason);
    }
  }
</script>

<main class="shell">
  <header>
    <div>
      <p class="eyebrow">BeBlog</p>
      <h1>Voice</h1>
    </div>
    <p class="status">{units.length} Absätze · Audio noch nicht gerendert</p>
  </header>

  {#if error}
    <p class="error" role="alert">{error}</p>
  {/if}

  <section class="workspace" aria-labelledby="manuscript-heading">
    <div class="section-heading">
      <div>
        <p class="label">MANUSKRIPT</p>
        <h2 id="manuscript-heading">Sprechtext</h2>
      </div>
      <p>Leerzeile = neue Render Unit</p>
    </div>

    <textarea
      bind:value={manuscript}
      oninput={manuscriptChanged}
      aria-label="Manuskript"
      disabled={loading}
    ></textarea>
  </section>

  <section class="workspace" aria-labelledby="units-heading">
    <div class="section-heading">
      <div>
        <p class="label">RENDER UNITS</p>
        <h2 id="units-heading">Absätze & Stimmen</h2>
      </div>
      <p>Stimme wird pro Absatz gewählt</p>
    </div>

    <div class="units">
      {#each units as unit (unit.id)}
        <article class="unit">
          <div class="unit-number">{unit.number}</div>
          <div class="unit-content">
            <p>{unit.text}</p>
            <span class="audio-state">{unit.audioState}</span>
          </div>
          <label>
            <span>Stimme</span>
            <select
              value={unit.voiceId}
              onchange={(event) => setUnitVoice(unit.id, event.currentTarget.value)}
            >
              <option value="thorsten-high">Thorsten High</option>
              <option value="thorsten-hessisch">Thorsten Hessisch</option>
            </select>
          </label>
        </article>
      {/each}
    </div>
  </section>
</main>

<style>
  :global(*) { box-sizing: border-box; }
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
    color: #202124;
    background: #f4f4f2;
  }
  .shell { max-width: 1120px; margin: 0 auto; padding: 42px; }
  header { display: flex; justify-content: space-between; align-items: end; margin-bottom: 28px; }
  .eyebrow, .label { margin: 0; font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: #777; }
  h1 { margin: 2px 0 0; font-size: 32px; font-weight: 650; }
  h2 { margin: 4px 0 0; font-size: 19px; font-weight: 600; }
  .status, .section-heading > p { margin: 0; color: #777; font-size: 13px; }
  .error { margin: 0 0 18px; padding: 12px 14px; border-radius: 10px; background: #fff; color: #8b2f2f; font-size: 13px; }
  .workspace { background: white; border-radius: 14px; padding: 22px; margin-bottom: 18px; }
  .section-heading { display: flex; justify-content: space-between; align-items: end; margin-bottom: 16px; }
  textarea {
    width: 100%; min-height: 220px; resize: vertical; border: 1px solid #d8d8d5;
    border-radius: 10px; padding: 16px; font: inherit; font-size: 16px; line-height: 1.55;
    background: #fff;
  }
  textarea:disabled { opacity: .6; }
  .units { display: grid; gap: 10px; }
  .unit { display: grid; grid-template-columns: 52px 1fr 190px; gap: 16px; align-items: center; padding: 15px 0; border-top: 1px solid #ececea; }
  .unit:first-child { border-top: 0; }
  .unit-number { font-variant-numeric: tabular-nums; color: #777; font-size: 13px; }
  .unit-content p { margin: 0 0 6px; line-height: 1.4; }
  .audio-state { font-size: 12px; color: #8a8a86; }
  label { display: grid; gap: 5px; font-size: 12px; color: #777; }
  select { width: 100%; border: 1px solid #d8d8d5; border-radius: 8px; background: white; padding: 8px 10px; font: inherit; color: #202124; }
</style>
