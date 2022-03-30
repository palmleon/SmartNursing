clear all
close all
clc
%% Library
import matlab.net.*
import matlab.net.http.*
%% Get request
r = RequestMessage;
uri = URI('https://api.thingspeak.com/channels.json?api_key=YTN43QRA4IWIEBIN');
resp = send(r,uri);
%% Retrive data
channel = resp.Body.Data(1);
data = thingSpeakRead(channel.id,'Fields',[1,2,3,4],NumPoints=8000,OutputFormat='matrix',ReadKey=channel.api_keys(2).api_key);
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


