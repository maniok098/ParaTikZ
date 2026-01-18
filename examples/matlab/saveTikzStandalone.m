function saveTikzStandalone(figHandle, figName)
% saveTikzStandalone generates a standalone .tex file for the given figure.
% 
%   saveTikzStandalone(figHandle, figName) takes in the figure handle and 
%   the desired name of the figure (figName), generates the corresponding standalone .tex file 
%   using matlab2tikz, and inserts necessary headers and footers.
%
%   Inputs:
%   figHandle - Handle of the figure to be saved as TikZ.
%   figName   - Desired name for the output .tex file.
%
% Example usage:
%   fig = figure;
%   plot(rand(10,1));
%   saveTikzStandalone(fig, 'RandomPlot');

% Generate .tex file using matlab2tikz
figure(figHandle);
matlab2tikz([figName, '.tex']);

disp(' ');
disp('Begin post-processing for standalone Tikz figure...');

% Read the generated .tex file
filename = [figName, '.tex'];
fileID = fopen(filename, 'r');
fileContents = fread(fileID, '*char')';
fclose(fileID);

% Define header and footer
header = [
"\documentclass[tikz]{standalone}"
""
"\usepackage{graphicx,pgfplots, pgfgantt, pdflscape, amsmath, tikz}"
"\pgfplotsset{compat=1.18}"
"\usetikzlibrary{arrows.meta,decorations.markings,patterns,positioning,bending,chains,calc,backgrounds,plotmarks,fit,shapes.misc}"
"\tikzset{>={Latex[width=2mm,length=2mm]}, font=\footnotesize}"
""
"\begin{document}"
""
];

footer = [
""
"\end{document}"
];


% Insert the command at the beginning and end of the file
newFileContents = strjoin([header; string(fileContents); footer], '\n');

% Write the modified content back to the .tex file
fileID = fopen(filename, 'w');
fwrite(fileID, newFileContents, 'char');
fclose(fileID);

disp(['Standalone Tikz figure saved successfully as ', filename]);

end
