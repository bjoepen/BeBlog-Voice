import { invoke } from "@tauri-apps/api/core";

export const projectBridge = {
  loadProjectState() {
    return invoke("load_project_state");
  },

  syncManuscript(manuscript) {
    return invoke("sync_manuscript", { manuscript });
  },

  setUnitVoice(unitId, voiceId) {
    return invoke("set_unit_voice", { unitId, voiceId });
  },
};

export const loadProjectState = () => projectBridge.loadProjectState();
export const syncManuscript = (manuscript) => projectBridge.syncManuscript(manuscript);
export const setUnitVoice = (unitId, voiceId) => projectBridge.setUnitVoice(unitId, voiceId);
