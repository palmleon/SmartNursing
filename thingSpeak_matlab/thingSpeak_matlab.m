% Template MATLAB code for visualizing data from a channel as a 2D line
% plot using PLOT function.

% Prior to running this MATLAB code template, assign the channel variables.
% Set 'readChannelID' to the channel ID of the channel to read from. 
% Also, assign the read field ID to 'fieldID1'. 

% TODO - Replace the [] with channel ID to read data from:
readChannelID = 1693205;
% TODO - Replace the [] with the Field ID to read data from:
fieldID1 = 1;

% Channel Read API Key 
% If your channel is private, then enter the read API
% Key between the '' below: 
readAPIKey = '6BOT4EPEGVUBWPWC';

%% Read Data %%
data = thingSpeakRead(1693205,'Fields',[2,3,4,6],NumPoints=8000,OutputFormat='matrix',ReadKey='6BOT4EPEGVUBWPWC')
% remove NaN data
for col=1:width(data)
    i = 1;
    for row=1:height(data)
        if ~isnan(data(row,col))
            n_data(i,col) = data(row,col)
            i = i+1;
        end
    end
end

%% Visualize Data %%
bar(10,2)
hold on
grid on
bar(1)
title("title")

