import LegalScaffold, { type LegalSection } from './LegalScaffold';

const SECTIONS: LegalSection[] = [
  {
    title: "Qu'est-ce qu'un cookie ?",
    hint: '',
    content: "Un cookie est un petit fichier texte déposé sur votre navigateur lors de la visite d'un site. Il permet de stocker des informations de session et de préférences."
  },
  {
    title: 'Cookies et stockage utilisés',
    hint: '',
    content: 'Cookie de session Django (sessionid) : nécessaire à l\'authentification. Token d\'authentification stocké dans le localStorage du navigateur pour maintenir la connexion entre les pages.'
  },
  {
    title: 'Finalité de chaque cookie',
    hint: '',
    content: 'sessionid : maintien de la session utilisateur (obligatoire technique). localStorage (token) : permet de rester connecté entre les pages. Aucun cookie de suivi publicitaire ou analytics.'
  },
  {
    title: 'Consentement',
    hint: '',
    content: 'Le cookie de session est strictement nécessaire au fonctionnement du service : aucun consentement préalable requis (exemption RGPD Art. 82). Le localStorage est utilisé à la seule initiative de l\'utilisateur via la connexion.'
  },
  {
    title: 'Durée de conservation',
    hint: '',
    content: 'sessionid : durée de la session (supprimé à la fermeture du navigateur). localStorage (token) : supprimé lors de la déconnexion manuelle ou de la suppression du compte.'
  },
  {
    title: 'Gérer ou refuser les cookies',
    hint: '',
    content: 'Paramètres navigateur : Chrome > Paramètres > Confidentialité et sécurité > Cookies. La suppression du cookie de session entraînera une déconnexion automatique.'
  }
];

export default function CookiesPage() {
  return (
    <LegalScaffold
      title="Politique de gestion des cookies"
      intro="Les cookies et technologies de stockage utilisés par le site, et comment les gérer."
      sections={SECTIONS}
      complete
    />
  );
}
