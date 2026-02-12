import WorkspaceForm from "./components/WorkspaceForm";
import CampaignForm from "./components/CampaignForm";
import CSVUpload from "./components/CSVUpload";
import M365Connect from "./components/M365Connect";

export default function App() {
  return (
    <div className="container">
      <h1>Salestroopz Desktop</h1>

      <WorkspaceForm />
      <M365Connect />
      <CSVUpload />
      <CampaignForm />
    </div>
  );
}
