/**
 * Appels API liés au RGPD (perturbation J3-bis).
 *
 * Export des données personnelles de l'utilisateur connecté (droit d'accès,
 * Article 15). Le backend renvoie un fichier téléchargeable (JSON ou CSV) ;
 * on déclenche le téléchargement côté navigateur via un Blob.
 */
import { api } from './client';

export type ExportFormat = 'json' | 'csv';

/** Télécharge l'export de mes données au format demandé (json | csv). */
export async function exportMyData(format: ExportFormat): Promise<void> {
  const response = await api.get('/accounts/me/export/', {
    // `fmt` et non `format` (réservé par DRF pour la négociation de contenu).
    params: { fmt: format },
    responseType: 'blob',
  });

  const contentType =
    (response.headers['content-type'] as string) ??
    (format === 'csv' ? 'text/csv' : 'application/json');
  const blob = new Blob([response.data], { type: contentType });

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `export-donnees.${format}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
