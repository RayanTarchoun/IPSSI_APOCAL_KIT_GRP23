import LegalScaffold, { type LegalSection } from './LegalScaffold';

const SECTIONS: LegalSection[] = [
  {
    title: 'Éditeur du site',
    hint: '',
    content: "EduTutor IA — Groupe 23, IPSSI. Projet pédagogique APOCAL'IPSSI 2026. Contact : equipe23@ipssi.edu."
  },
  {
    title: 'Directeur de la publication',
    hint: '',
    content: 'Rayan TARCHOUN, Scrum Master du Groupe 23 — IPSSI.'
  },
  {
    title: 'Hébergeur',
    hint: '',
    content: "Solution de conteneurisation locale Docker Desktop. Données hébergées exclusivement sur le serveur local de l'équipe (France). Aucun service cloud tiers."
  },
  {
    title: 'Propriété intellectuelle',
    hint: '',
    content: "Code source : APOCAL'IPSSI 2026 © Mohamed EL AFRIT — Licence libre. Contenus déposés par les utilisateurs : ceux-ci conservent l'intégralité de leurs droits."
  },
  {
    title: 'Contact',
    hint: '',
    content: 'Pour toute question juridique : equipe23@ipssi.edu.'
  }
];

export default function MentionsLegalesPage() {
  return (
    <LegalScaffold
      title="Mentions légales"
      intro="Informations légales obligatoires identifiant l'éditeur et l'hébergeur du site."
      sections={SECTIONS}
      complete
    />
  );
}
